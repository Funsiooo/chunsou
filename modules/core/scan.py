# -*- coding: utf-8 -*-

'''
@File    ：scan.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

import json
from urllib.request import urlopen
import ipaddress

import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
from modules.core.color import Colors
from modules.core.time import print_start_time, print_end_time, current_time
from modules.core.args import argument
from modules.core.agent import User_Agent
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from modules.core.proxy import proxies
import threading
import chardet
import urllib.parse
import concurrent.futures
from Wappalyzer import Wappalyzer, WebPage
from modules.core.threads import num_threads
from modules.core.output import script_start, script_end, output_dir, scan_save_to_excle
from modules.core.icon import get_ico_url, get_hash


'''
Single_scan
'''
def scan_rule(url):
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)
    headers = User_Agent()
    response = requests.get(url, headers=headers, timeout=5, verify=False, proxies=proxies(), allow_redirects=False)
    content = response.content
    encoding = chardet.detect(content)['encoding']

    try:
        if encoding != 'utf-8':
            html_text = content.decode('gbk')
        else:
            html_text = content.decode(encoding)
    except Exception as e:
        html_text = None

    header_string = str(response.headers)
    status_code = response.status_code

    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        page_title = soup.find("title")
        title = page_title.get_text().strip()
    except Exception as e:
        title = None

    if status_code == 200:
        status_code = status_code
        if title is None or len(title) == 0:
            title = None

    elif status_code == 302:
        redirected_url = response.url
        redirected_response = requests.get(redirected_url, headers=headers, verify=False, timeout=5)

        if redirected_response.status_code == 200:
            soup = BeautifulSoup(redirected_response.content, 'html.parser')
            page_title = soup.find('title')

            try:
                title = page_title.get_text().strip()
            except Exception as e:
                title = None

            status_code = status_code

            if title is None or len(title) == 0:
                title = None

    else:
        status_code = status_code
        if title is None or len(title) == 0:
            title = None

    # 优化 icon_hash 报错
    try:
        ico_content = requests.get(url=get_ico_url(url), headers=headers, timeout=5, verify=False).content
        if not ico_content:
            print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}"
          f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET}")
        else:
            ico_hash = get_hash(ico_content)
    except requests.exceptions.RequestException as e:
        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}"
          f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET}{Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET}")

    with open('modules/config/finger.json', 'r', encoding='utf-8') as file:
        fingerprint = json.load(file)

    try:
        for fingerprints in fingerprint['fingerprint']:
            cms = fingerprints['cms']
            method = fingerprints['method']
            location = fingerprints['location']
            keywords = fingerprints['keyword']

            if html_text is not None:
                if method == 'keyword' and location == 'body':
                    found_keywords = all(keyword in html_text for keyword in keywords)
                    if found_keywords:
                        return cms, status_code, title

                elif method == 'icon_hash' and location == 'body':
                    found_keywords = all(keyword in ico_hash for keyword in keywords)
                    if found_keywords:
                        return cms, status_code, title

                elif method == 'keyword' and location == 'header':
                    for keyword in keywords:
                        if keyword in header_string:
                            return cms, status_code, title

                elif title is not None:
                    if method == 'keyword' and location == 'title':
                        found_keywords = all(keyword in title for keyword in keywords)
                        if found_keywords:
                            return cms, status_code, title

        return None, status_code, title
    except Exception as e:
        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}"
          f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET}")

def single_main():
    args = argument()

    url = args.url

    out_file = output_dir()

    excle_results = []


    script_start()

    try:
        global final_key
        try:
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            warnings.filterwarnings("ignore", category=UserWarning,
                                    message="Caught 'unbalanced parenthesis at position 119'")
            warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
            warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

            webpage = WebPage.new_from_url(url, verify=False, timeout=5)

            wappalyzer = Wappalyzer.latest()
            wappalyzer.analyze(webpage)
            results = wappalyzer.analyze_with_categories(webpage)

            key_list = list(results.keys())

            if key_list:
                final_key = str(key_list).replace('[', '').replace(']', '').replace("'", '')
            else:
                final_key = "None"

        except Exception as e:
            final_key = None

        if out_file.endswith(".txt"):
            try:
                detected_cms, status_code, title = scan_rule(url)

                with open(out_file, 'w') as file:
                    if detected_cms:
                        result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                 f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET}" \
                                 f" {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{detected_cms}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{title}" \
                                 f"{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{final_key}{Colors.RESET}"

                        write_result = f"[+] [{status_code}] {url} | {detected_cms} | {title} | {final_key}"

                    else:
                        result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                 f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} " \
                                 f"{Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{title}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} " \
                                 f"{Colors.YELLOW_B}{final_key}{Colors.RESET}"

                        write_result = f"[+] [{status_code}] {url} | {detected_cms} | {title} | {final_key}"

                    print(result)
                    file.write(write_result + '\n')

            except Exception as e:
                status_code = 404
                error_result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                               f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET}" \
                               f"{Colors.RED} [{str(e)}] {Colors.RESET}"

                error_write_result = f"[-] {url} [{str(e)}]"

                print(error_result)
                file.write(error_write_result + '\n')

            script_end()


        elif out_file.endswith(".xlsx"):
            try:
                detected_cms, status_code, title = scan_rule(url)

                if detected_cms:
                    result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                             f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} [{url}]" \
                             f" {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW}{detected_cms}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW}{title}" \
                             f"{Colors.YELLOW} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW}{final_key}{Colors.RESET}"

                    write_result = status_code, url, title, final_key, detected_cms
                    excle_results.append(write_result)

                else:
                    result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                             f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}] [{url}] " \
                             f"{Colors.WHITE}|{Colors.RESET} {Colors.YELLOW}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW}{title}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} " \
                             f"{Colors.YELLOW}{final_key}{Colors.RESET}"

                    write_result = status_code, url, title, final_key, detected_cms
                    excle_results.append(write_result)

                print(result)

            except Exception as e:
                status_code = 404

                whoami = ' '
                iamhahaha = ' '

                error_result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                               f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {url}" \
                               f"{Colors.RED} {Colors.WHITE}[{Colors.RESET}{str(e)}{Colors.WHITE}]{Colors.RESET} {Colors.RESET}"

                write_result = status_code, url, whoami, iamhahaha, str(e)
                excle_results.append(write_result)

                print(error_result)

            script_end()

            scan_save_to_excle(excle_results)

    except Exception as e:
        pass


def lists_filename(file):
    urls = []

    with open(file, 'r', encoding='utf-8') as f:
        target = [line.strip() for line in f]

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
    excle_results = []
    args = argument()

    try:
        urls = lists_filename(file)

        out_file = output_dir()

        script_start()

        lock = threading.Lock()

        if out_file.endswith(".txt"):
            with open(out_file, 'w') as file:
                with lock:
                    def scan_url(url):
                        global final_key
                        try:
                            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
                            warnings.filterwarnings("ignore", category=UserWarning,
                                                    message="Caught 'unbalanced parenthesis at position 119'")

                            warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

                            warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

                            webpage = WebPage.new_from_url(url, verify=False, timeout=3)

                            wappalyzer = Wappalyzer.latest()
                            wappalyzer.analyze(webpage)
                            results = wappalyzer.analyze_with_categories(webpage)

                            key_list = list(results.keys())

                            if key_list:
                                final_key = str(key_list).replace('[', '').replace(']', '').replace("'", '')
                            else:
                                final_key = "None"

                        except Exception as e:
                            final_key = None

                        try:
                            detected_cms, status_code, title = scan_rule(url)

                            if detected_cms:
                                result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                         f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET}" \
                                         f" {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{detected_cms}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{title}" \
                                         f"{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{final_key}{Colors.RESET}"

                                write_result = f"[+] [{status_code}] {url} | {detected_cms} | {title} | {final_key}"
                            else:
                                result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                         f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} " \
                                         f" {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{title}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} " \
                                         f"{Colors.YELLOW_B}{final_key}{Colors.RESET}"
                                write_result = f"[+] [{status_code}] {url} | None | {title} | {final_key}"

                            print(result)
                            with open(out_file, 'a') as file:
                                file.write(write_result + '\n')

                        except Exception as e:
                            status_code = 404
                            error_result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                           f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET}" \
                                           f"{Colors.RED} [{str(e)}] {Colors.RESET}"

                            error_write_result = f"[-] [{status_code}] {url} [{str(e)}]"

                            if args.e:
                                print(error_result)
                                with open(out_file, 'a') as file:
                                    file.write(error_write_result + '\n')

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads()) as executor_threads:
                futures = [executor_threads.submit(scan_url, url) for url in urls]
                concurrent.futures.wait(futures)

            script_end()


        elif out_file.endswith(".xlsx"):
            with lock:
                def scan_url(url):
                    global final_key
                    try:
                        warnings.filterwarnings('ignore', category=InsecureRequestWarning)
                        warnings.filterwarnings("ignore", category=UserWarning,
                                                message="Caught 'unbalanced parenthesis at position 119'")
                        warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

                        warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

                        webpage = WebPage.new_from_url(url, verify=False, timeout=3)

                        wappalyzer = Wappalyzer.latest()
                        wappalyzer.analyze(webpage)
                        results = wappalyzer.analyze_with_categories(webpage)

                        key_list = list(results.keys())

                        if key_list:
                            final_key = str(key_list).replace('[', '').replace(']', '').replace("'", '')
                        else:
                            final_key = "None"

                    except Exception as e:
                        final_key = None

                    try:
                        detected_cms, status_code, title = scan_rule(url)

                        if detected_cms:
                            result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                     f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET}" \
                                     f" {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{detected_cms}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{title}" \
                                     f"{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{final_key}{Colors.RESET}"

                            write_result = status_code, url, title, final_key, detected_cms
                            excle_results.append(write_result)

                        else:
                            result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                     f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} " \
                                     f" {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}None{Colors.RESET} {Colors.WHITE}|{Colors.RESET} {Colors.YELLOW_B}{title}{Colors.RESET} {Colors.WHITE}|{Colors.RESET} " \
                                     f"{Colors.YELLOW_B}{final_key}{Colors.RESET}"

                            write_result = status_code, url, title, final_key, detected_cms
                            excle_results.append(write_result)

                        print(result)


                    except Exception as e:
                        status_code = 404

                        whoami = ' '
                        iamhahaha = ' '

                        error_result = f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET}" \
                                       f" {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {url}" \
                                       f"{Colors.RED} [{str(e)}] {Colors.RESET}"

                        if args.e:
                            write_result = status_code, url, whoami, iamhahaha, str(e)
                            excle_results.append(write_result)

                    if args.e:
                        print(error_result)

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads()) as executor_threads:
                futures = [executor_threads.submit(scan_url, url) for url in urls]
                concurrent.futures.wait(futures)

            script_end()
            scan_save_to_excle(excle_results)

    except Exception as e:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}{Colors.RED}[-] Error occurred , Check whether the "
              f"network, command, or configuration is correct")
