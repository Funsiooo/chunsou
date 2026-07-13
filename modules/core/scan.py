# -*- coding: utf-8 -*-

'''
@File    ：scan.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

import concurrent.futures
import ipaddress
import json
import os
import re
import threading
import warnings
from urllib.parse import urlparse

import chardet
import requests
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"pkg_resources is deprecated as an API\..*"
)
from Wappalyzer import Wappalyzer, WebPage
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from urllib3.exceptions import InsecureRequestWarning

from modules.api.ai import analyze_page
from modules.core.agent import User_Agent
from modules.core.args import argument
from modules.core.color import Colors
from modules.core.icon import get_hash, get_ico_url
from modules.core.output import output_dir, scan_save_to_excle, script_end, script_start
from modules.core.proxy import proxies
from modules.core.threads import num_threads
from modules.core.time import print_start_time


warnings.filterwarnings('ignore', category=InsecureRequestWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
warnings.filterwarnings("ignore", category=UserWarning,
                        message="Caught 'unbalanced parenthesis at position 119'")

_THREAD_LOCAL = threading.local()
_CACHE_LOCK = threading.Lock()
_FINGERPRINTS = None
_WAPPALYZER = None
_PROXY_CONFIG = None
_FINGERPRINT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'finger.json')
_HEADER_KEYS = ('server', 'x-powered-by', 'set-cookie', 'www-authenticate', 'location', 'via')
_TEXT_STOPWORDS = {
    'http', 'https', 'www', 'com', '登录', '系统', '平台', '首页', '欢迎', '请输入', '用户名',
    '密码', '验证码', '版权所有', 'copyright', 'admin', 'index', 'true', 'false'
}


def _get_session():
    # 线程内复用会话，减少重复建连。
    session = getattr(_THREAD_LOCAL, 'session', None)
    if session is None:
        session = requests.Session()
        _THREAD_LOCAL.session = session
    return session


def _load_fingerprints():
    global _FINGERPRINTS
    if _FINGERPRINTS is None:
        with _CACHE_LOCK:
            if _FINGERPRINTS is None:
                with open(_FINGERPRINT_PATH, 'r', encoding='utf-8') as file:
                    _FINGERPRINTS = json.load(file).get('fingerprint', [])
    return _FINGERPRINTS


def _get_wappalyzer():
    global _WAPPALYZER
    if _WAPPALYZER is None:
        with _CACHE_LOCK:
            if _WAPPALYZER is None:
                _WAPPALYZER = Wappalyzer.latest()
    return _WAPPALYZER


def _get_proxy_config():
    global _PROXY_CONFIG
    if _PROXY_CONFIG is None:
        with _CACHE_LOCK:
            if _PROXY_CONFIG is None:
                _PROXY_CONFIG = proxies()
    return _PROXY_CONFIG


def _display_value(value):
    if value is None or value == '':
        return 'None'
    return value


def _truncate_text(text, limit):
    if text is None:
        return None
    clean_text = ' '.join(str(text).split())
    if len(clean_text) <= limit:
        return clean_text
    return clean_text[:limit].rstrip() + '...'


def _dedupe_keep_order(items):
    unique_items = []
    seen = set()
    for item in items:
        clean_item = item.strip()
        if not clean_item or clean_item in seen:
            continue
        seen.add(clean_item)
        unique_items.append(clean_item)
    return unique_items


def _decode_response_content(response):
    content = response.content
    if not content:
        return None

    candidates = []
    if response.encoding:
        candidates.append(response.encoding)

    apparent_encoding = getattr(response, 'apparent_encoding', None)
    if apparent_encoding and apparent_encoding not in candidates:
        candidates.append(apparent_encoding)

    detected = chardet.detect(content).get('encoding')
    if detected and detected not in candidates:
        candidates.append(detected)

    for encoding in ('utf-8', 'gb18030', 'gbk'):
        if encoding not in candidates:
            candidates.append(encoding)

    for encoding in candidates:
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, LookupError, TypeError):
            continue

    return content.decode('utf-8', errors='ignore')


def _extract_title(html_text):
    if not html_text:
        return None

    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        page_title = soup.find("title")
        if page_title is None:
            return None
        title = page_title.get_text().strip()
        return title or None
    except Exception:
        return None


def _clean_page_text(html_text):
    if not html_text:
        return ''

    soup = BeautifulSoup(html_text, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()

    text = soup.get_text('\n', strip=True)
    text = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', ' ', text)
    text = re.sub(r'[ \t\r\f\v]+', ' ', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)


def _extract_body_snippets(clean_text, limit=4):
    snippets = []
    for line in clean_text.split('\n'):
        compact_line = ' '.join(line.split())
        if 2 <= len(compact_line) <= 80:
            snippets.append(compact_line)
    return _dedupe_keep_order(snippets)[:limit]


def _extract_body_keywords(url, title, clean_text, limit=12):
    parsed_url = urlparse(url)
    path_tokens = re.findall(r'[A-Za-z0-9_-]{2,30}', parsed_url.path)
    source_text = '\n'.join([title or '', ' '.join(path_tokens), clean_text[:1000]])
    candidates = re.findall(r'[\u4e00-\u9fffA-Za-z0-9._-]{2,40}', source_text)

    keywords = []
    for candidate in candidates:
        lowered = candidate.lower()
        if lowered in _TEXT_STOPWORDS:
            continue
        if candidate.isdigit():
            continue
        keywords.append(candidate)

    return _dedupe_keep_order(keywords)[:limit]


def _extract_dom_features(html_text):
    if not html_text:
        return {}

    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        forms = soup.find_all('form')
        buttons = soup.find_all(['button', 'input'])

        field_labels = []
        for tag in soup.find_all(['input', 'textarea']):
            candidate = tag.get('placeholder') or tag.get('name') or tag.get('id')
            if candidate:
                field_labels.append(candidate.strip())

        button_texts = []
        for tag in buttons:
            candidate = tag.get_text(strip=True) or tag.get('value') or ''
            if candidate:
                button_texts.append(candidate.strip())

        return {
            'has_login_form': bool(forms),
            'form_field_labels': _dedupe_keep_order(field_labels)[:3],
            'button_texts': _dedupe_keep_order(button_texts)[:3]
        }
    except Exception:
        return {}


def _summarize_headers(headers):
    header_summary = {}
    for key in _HEADER_KEYS:
        if key not in headers:
            continue

        value = headers.get(key, '')
        if key == 'set-cookie':
            cookie_names = []
            raw_headers = getattr(headers, 'get_all', None)
            if callable(raw_headers):
                cookie_lines = raw_headers('Set-Cookie', [])
            else:
                cookie_value = headers.get('set-cookie', '') or headers.get('Set-Cookie', '')
                cookie_lines = re.split(r',\s*(?=[A-Za-z0-9!#$%&\'*+.^_`|~-]+=)', str(cookie_value)) if cookie_value else []

            for cookie_line in cookie_lines:
                cookie_name = str(cookie_line).split('=', 1)[0].strip()
                if cookie_name:
                    cookie_names.append(cookie_name)
            header_summary[key] = _dedupe_keep_order(cookie_names)[:5]
            continue

        compact_value = ' '.join(str(value).split())
        header_summary[key] = _truncate_text(compact_value, 120)

    return header_summary


def _fetch_ico_hash(url, html_text, headers, timeout):
    try:
        icon_url = get_ico_url(url, html_text=html_text)
        if not icon_url:
            return None

        response = _get_session().get(
            icon_url,
            headers=headers,
            timeout=timeout,
            verify=False,
            proxies=_get_proxy_config(),
            allow_redirects=True
        )
        if not response.content:
            return None
        return get_hash(response.content)
    except requests.RequestException:
        return None


def _match_fingerprint(html_text, title, header_string, ico_hash):
    for fingerprint in _load_fingerprints():
        cms = fingerprint.get('cms')
        method = fingerprint.get('method')
        location = fingerprint.get('location')
        keywords = fingerprint.get('keyword', [])

        if method == 'keyword' and location == 'body' and html_text:
            if all(keyword in html_text for keyword in keywords):
                return cms

        elif method == 'icon_hash' and location == 'body' and ico_hash:
            if all(keyword in ico_hash for keyword in keywords):
                return cms

        elif method == 'keyword' and location in ('header', 'banner') and header_string:
            if any(keyword in header_string for keyword in keywords):
                return cms

        elif method == 'keyword' and location == 'title' and title:
            if all(keyword in title for keyword in keywords):
                return cms

    return None


def _detect_stack(url, timeout):
    try:
        webpage = WebPage.new_from_url(url, verify=False, timeout=timeout)
        results = _get_wappalyzer().analyze_with_categories(webpage)
        key_list = list(results.keys())
        return ', '.join(key_list[:5]) if key_list else 'None'
    except Exception:
        return None


def _build_ai_auto_evidence(result):
    return {
        'mode': 'auto',
        'url': result['url'],
        'final_url': result.get('final_url') or result['url'],
        'status_code': result['status_code'],
        'title': result.get('title') or '',
        'favicon_hash': result.get('favicon_hash') or '',
        'tech_stack': result.get('stack_list', []),
        'headers_summary': result.get('headers_summary', {}),
        'body_keywords': result.get('body_keywords', [])[:8],
        'local_fingerprint': result.get('detected_cms') or '',
        'local_candidates': result.get('local_candidates', [])[:3]
    }


def _build_ai_force_evidence(result):
    return {
        'mode': 'force',
        'url': result['url'],
        'final_url': result.get('final_url') or result['url'],
        'status_code': result['status_code'],
        'title': result.get('title') or '',
        'favicon_hash': result.get('favicon_hash') or '',
        'tech_stack': result.get('stack_list', []),
        'headers_summary': result.get('headers_summary', {}),
        'body_keywords': result.get('body_keywords', [])[:12],
        'body_snippets': result.get('body_snippets', [])[:4],
        'dom_features': result.get('dom_features', {}),
        'local_fingerprint': result.get('detected_cms') or '',
        'local_candidates': result.get('local_candidates', [])[:3]
    }


def _apply_ai_analysis(result, args):
    ai_mode = getattr(args, 'ai', None)
    if not ai_mode:
        return result

    if ai_mode == 'auto' and result.get('detected_cms'):
        return result

    # 只把当前页面的摘要交给语义分析，避免无关内容放大干扰。
    if ai_mode == 'force':
        evidence = _build_ai_force_evidence(result)
    else:
        evidence = _build_ai_auto_evidence(result)

    ai_result = analyze_page(
        evidence,
        mode=ai_mode,
        provider=getattr(args, 'ai_provider', None),
        model=getattr(args, 'ai_model', None)
    )

    result['ai_mode'] = ai_mode
    result['ai_provider'] = ai_result.get('provider')
    result['ai_model'] = ai_result.get('model')
    result['ai_cache_hit'] = ai_result.get('cache_hit', False)

    if ai_result.get('error'):
        result['ai_error'] = ai_result['error']
        if ai_mode == 'force':
            result['ai_analysis'] = _truncate_text(f"AI分析失败：{ai_result['error']}", 160)
        return result

    if ai_mode == 'force':
        result['ai_analysis'] = _truncate_text(ai_result.get('analysis') or '当前页面特征不足，建议人工复核', 80)
        return result

    fingerprint = (ai_result.get('fingerprint') or '').strip()
    if fingerprint and fingerprint.lower() != 'unknown':
        result['ai_fingerprint'] = fingerprint
        result['ai_confidence'] = ai_result.get('confidence')
        result['ai_evidence'] = ai_result.get('evidence', [])[:3]

    return result


def scan_rule(url, timeout=5):
    headers = User_Agent()
    response = _get_session().get(
        url,
        headers=headers,
        timeout=timeout,
        verify=False,
        proxies=_get_proxy_config(),
        allow_redirects=False
    )

    html_text = _decode_response_content(response)
    clean_text = _clean_page_text(html_text)
    title = _extract_title(html_text)
    header_string = str(response.headers)
    status_code = response.status_code
    ico_hash = _fetch_ico_hash(url, html_text, headers, timeout)
    detected_cms = _match_fingerprint(html_text, title, header_string, ico_hash)
    body_snippets = _extract_body_snippets(clean_text, limit=4)
    body_keywords = _extract_body_keywords(url, title, clean_text, limit=12)

    result = {
        'url': url,
        'final_url': response.url,
        'status_code': status_code,
        'title': title,
        'detected_cms': detected_cms,
        'favicon_hash': ico_hash,
        'headers_summary': _summarize_headers(response.headers),
        'body_keywords': body_keywords,
        'body_snippets': body_snippets,
        'dom_features': _extract_dom_features(html_text),
        'local_candidates': [detected_cms] if detected_cms else []
    }
    return result


def analyze_target(url, timeout=5, args=None):
    scan_result = scan_rule(url, timeout=timeout)
    stack = _detect_stack(url, timeout)
    scan_result['stack'] = stack
    scan_result['stack_list'] = [item.strip() for item in (stack or '').split(',') if item.strip()]

    if args:
        scan_result = _apply_ai_analysis(scan_result, args)

    return scan_result


def _get_fingerprint_output(result):
    if result.get('ai_mode') == 'auto' and result.get('ai_fingerprint'):
        return f"AI识别结果：{result['ai_fingerprint']}"
    return _display_value(result.get('detected_cms'))


def _get_force_analysis_output(result):
    analysis = result.get('ai_analysis') or '当前页面特征不足，建议人工复核'
    return f"AI分析结果：{analysis}"


def _format_success_console(result):
    if result.get('ai_mode') == 'force':
        return (
            f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]"
            f"{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]"
            f"{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{result['status_code']}{Colors.RESET}"
            f"{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{result['url']}{Colors.RESET} {Colors.WHITE}|"
            f"{Colors.RESET} {Colors.YELLOW_B}{_get_force_analysis_output(result)}{Colors.RESET}"
        )

    return (
        f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]"
        f"{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]"
        f"{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{result['status_code']}{Colors.RESET}"
        f"{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{result['url']}{Colors.RESET} {Colors.WHITE}|"
        f"{Colors.RESET} {Colors.YELLOW_B}{_get_fingerprint_output(result)}{Colors.RESET} "
        f"{Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{_display_value(result.get('title'))}{Colors.RESET} "
        f"{Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{_display_value(result.get('stack'))}{Colors.RESET}"
    )


def _format_error_console(result):
    return (
        f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]"
        f"{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]"
        f"{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{result['status_code']}{Colors.RESET}"
        f"{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{result['url']}{Colors.RESET}"
        f"{Colors.RED} [{result['error']}] {Colors.RESET}"
    )


def _format_text_line(result):
    if result.get('ai_mode') == 'force':
        return f"{result['url']} | {_get_force_analysis_output(result)}"

    return (
        f"[+] [{result['status_code']}] {result['url']} | {_get_fingerprint_output(result)} | "
        f"{_display_value(result.get('title'))} | {_display_value(result.get('stack'))}"
    )


def _format_error_line(result):
    return f"[-] [{result['status_code']}] {result['url']} [{result['error']}]"


def _get_excel_headers(result):
    if result.get('ai_mode') == 'force':
        return ['网页URL', 'AI分析结果']
    return ['状态码', '网页URL', '网页标题', '网站技术栈', '指纹结果']


def _format_excel_row(result):
    if result.get('ai_mode') == 'force':
        return (
            result['url'],
            _get_force_analysis_output(result)
        )

    return (
        result['status_code'],
        result['url'],
        _display_value(result.get('title')),
        _display_value(result.get('stack')),
        _get_fingerprint_output(result)
    )


def _scan_worker(url, timeout, args):
    try:
        return analyze_target(url, timeout=timeout, args=args)
    except Exception as exc:
        result = {
            'url': url,
            'status_code': 404,
            'title': None,
            'detected_cms': None,
            'stack': None,
            'error': str(exc),
        }
        if getattr(args, 'ai', None) == 'force':
            result['ai_mode'] = 'force'
            result['ai_analysis'] = _truncate_text(f"AI分析失败：{str(exc)}", 160)
        return result


def _handle_single_result(result, out_file, args):
    if out_file.endswith('.txt'):
        with open(out_file, 'w', encoding='utf-8') as file:
            if result.get('error') and getattr(args, 'ai', None) != 'force':
                print(_format_error_console(result))
                file.write(_format_error_line(result) + '\n')
            else:
                print(_format_success_console(result))
                file.write(_format_text_line(result) + '\n')
        return

    if out_file.endswith('.xlsx'):
        if result.get('error') and getattr(args, 'ai', None) != 'force':
            rows = [(result['status_code'], result['url'], ' ', ' ', result['error'])]
            headers = ['状态码', '网页URL', '网页标题', '网站技术栈', '指纹结果']
            print(_format_error_console(result))
        else:
            rows = [_format_excel_row(result)]
            headers = _get_excel_headers(result)
            print(_format_success_console(result))
        scan_save_to_excle(rows, csv_headers=headers)


def single_main():
    args = argument()
    url = args.url
    out_file = output_dir()

    script_start()
    result = _scan_worker(url, timeout=5, args=args)
    _handle_single_result(result, out_file, args)
    script_end()


def lists_filename(file):
    urls = []

    with open(file, 'r', encoding='utf-8') as f:
        target = [line.strip() for line in f if line.strip()]

        for url in target:
            if '/' in url:
                try:
                    network = ipaddress.ip_network(url, strict=False)
                    for ip in network:
                        url_http = 'http://' + str(ip)
                        url_https = 'https://' + str(ip)
                        urls.append(url_http)
                        urls.append(url_https)
                except ValueError:
                    urls.append(url)
            elif '-' in url:
                try:
                    start_ip, end_ip = url.split('-')
                    start_ip_obj = ipaddress.ip_address(start_ip.strip())
                    end_ip_obj = ipaddress.ip_address(end_ip.strip())
                    for ip in range(int(start_ip_obj), int(end_ip_obj) + 1):
                        url_http = 'http://' + str(ipaddress.ip_address(ip))
                        url_https = 'https://' + str(ipaddress.ip_address(ip))
                        urls.append(url_http)
                        urls.append(url_https)
                except ValueError:
                    urls.append(url)
            else:
                if not url.startswith(('http://', 'https://')):
                    url_http = 'http://' + url
                    url_https = 'https://' + url
                    urls.append(url_http)
                    urls.append(url_https)
                else:
                    urls.append(url)

    return urls


def lists_main(file):
    args = argument()
    urls = lists_filename(file)
    out_file = output_dir()
    excel_results = []
    excel_headers = None

    script_start()

    try:
        if out_file.endswith('.txt'):
            with open(out_file, 'w', encoding='utf-8') as txt_file:
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads()) as executor_threads:
                    future_map = {
                        executor_threads.submit(_scan_worker, url, 3, args): url for url in urls
                    }
                    for future in concurrent.futures.as_completed(future_map):
                        result = future.result()

                        if result.get('error') and getattr(args, 'ai', None) != 'force':
                            if args.e:
                                print(_format_error_console(result))
                                txt_file.write(_format_error_line(result) + '\n')
                            continue

                        print(_format_success_console(result))
                        txt_file.write(_format_text_line(result) + '\n')

        elif out_file.endswith('.xlsx'):
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads()) as executor_threads:
                future_map = {
                    executor_threads.submit(_scan_worker, url, 3, args): url for url in urls
                }
                for future in concurrent.futures.as_completed(future_map):
                    result = future.result()

                    if result.get('error') and getattr(args, 'ai', None) != 'force':
                        if args.e:
                            print(_format_error_console(result))
                            excel_results.append((result['status_code'], result['url'], ' ', ' ', result['error']))
                            excel_headers = excel_headers or ['状态码', '网页URL', '网页标题', '网站技术栈', '指纹结果']
                        continue

                    print(_format_success_console(result))
                    excel_results.append(_format_excel_row(result))
                    excel_headers = excel_headers or _get_excel_headers(result)

            if excel_results:
                scan_save_to_excle(excel_results, csv_headers=excel_headers)

        script_end()

    except Exception:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}{Colors.RED}[-] Error occurred , Check whether the "
              f"network, command, or configuration is correct")
