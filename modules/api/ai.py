# -*- coding: utf-8 -*-

import configparser
import hashlib
import json
import os

from openai import OpenAI


CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')
CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'results', 'ai_cache.json')


def _read_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    return config


def _get_option(config, section, option, fallback=''):
    if config.has_option(section, option):
        return config.get(section, option).strip('"')
    return fallback


def _load_settings(provider=None, model=None):
    config = _read_config()
    selected_provider = provider or _get_option(config, 'ai', 'provider', 'gpt') or 'gpt'
    timeout = int(_get_option(config, 'ai', 'timeout', '20') or '20')
    cache_enabled = (_get_option(config, 'ai', 'cache', 'true') or 'true').lower() == 'true'

    if selected_provider == 'deepseek':
        base_url = _get_option(config, 'deepseek_api', 'base_url', 'https://api.deepseek.com')
        api_key = _get_option(config, 'deepseek_api', 'api_key', '')
        default_model = _get_option(config, 'deepseek_api', 'model', 'deepseek-v4-pro')
    else:
        selected_provider = 'gpt'
        base_url = _get_option(config, 'gpt_api', 'base_url', 'https://api.openai.com/v1')
        api_key = _get_option(config, 'gpt_api', 'api_key', '')
        default_model = _get_option(config, 'ai', 'model', 'gpt-5.5')

    return {
        'provider': selected_provider,
        'model': model or default_model,
        'base_url': base_url,
        'api_key': api_key,
        'timeout': timeout,
        'cache_enabled': cache_enabled,
        'max_tokens_auto': int(_get_option(config, 'ai', 'max_output_tokens_auto', '120') or '120'),
        'max_tokens_force': int(_get_option(config, 'ai', 'max_output_tokens_force', '180') or '180')
    }


def _ensure_cache_dir():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}

    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as cache_file:
            return json.load(cache_file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache_data):
    _ensure_cache_dir()
    with open(CACHE_PATH, 'w', encoding='utf-8') as cache_file:
        json.dump(cache_data, cache_file, ensure_ascii=False, indent=2)


def _build_cache_key(mode, provider, model, evidence):
    # 相同页面摘要只请求一次，减少重复消耗。
    payload = {
        'mode': mode,
        'provider': provider,
        'model': model,
        'evidence': evidence
    }
    raw_data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()


def _strip_json_text(raw_text):
    content = raw_text.strip()
    if content.startswith('```'):
        content = content.strip('`')
        if content.startswith('json'):
            content = content[4:].strip()
    start_index = content.find('{')
    end_index = content.rfind('}')
    if start_index != -1 and end_index != -1:
        return content[start_index:end_index + 1]
    return content


def _auto_system_prompt():
    return (
        "你是一个 Web 指纹识别助手，擅长根据网页标题、响应头、favicon hash、技术栈和少量正文关键词判断最可能的产品指纹。\n"
        "任务要求：\n"
        "1. 仅根据当前页面摘要证据判断最可能的产品名称。\n"
        "2. 如果证据不足，返回 unknown。\n"
        "3. 不要输出长解释。\n"
        "4. 只返回 JSON。\n"
        "5. fingerprint 必须简洁，例如：致远OA、Nacos、禅道、帆软报表。\n"
        "6. confidence 取值范围为 0 到 1。\n"
        "7. evidence 最多返回 3 条。"
    )


def _force_system_prompt():
    return (
        "你是一个 Web 页面分析助手。\n"
        "你只能根据当前 URL 返回的这个页面本身进行分析。\n"
        "允许将当前输入 URL 与最终落地 URL 的路径特征作为判断依据。\n"
        "不得根据页面中出现的其他 URL、接口地址、跳转链接、iframe 目标地址或未访问页面内容进行推断。\n"
        "不得扩展分析整个站点，只能分析当前页面。\n"
        "任务要求：\n"
        "1. 对当前页面做整体语义分析。\n"
        "2. 输出一条简短中文分析结果，不超过 80 个汉字。\n"
        "3. 如果证据不足，也要给出保守分析结果。\n"
        "4. 只返回 JSON。\n"
        "5. analysis 必须是可直接展示给用户的结果。"
    )


def _build_messages(evidence, mode):
    if mode == 'force':
        system_prompt = _force_system_prompt()
        user_prompt = (
            "请仅基于当前 URL 返回页面本身的证据进行分析，不要参考页面中的其他 URL 或未访问页面。\n\n"
            f"输入：\n{json.dumps(evidence, ensure_ascii=False, indent=2)}\n\n"
            "输出要求：\n"
            "只返回以下 JSON，不要输出任何额外内容：\n"
            "{\n"
            '  "analysis": "一句简短中文分析结果，不超过80字"\n'
            "}"
        )
    else:
        system_prompt = _auto_system_prompt()
        user_prompt = (
            "请根据以下当前页面摘要证据判断最可能的产品指纹。\n\n"
            f"输入：\n{json.dumps(evidence, ensure_ascii=False, indent=2)}\n\n"
            "输出要求：\n"
            "只返回以下 JSON，不要输出任何额外内容：\n"
            "{\n"
            '  "fingerprint": "产品名称或unknown",\n'
            '  "confidence": 0.00,\n'
            '  "evidence": ["最多3条简短证据"]\n'
            "}"
        )

    return [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]


def _build_response_input(messages):
    blocks = []
    for message in messages:
        role = message.get('role', 'user')
        content = message.get('content', '')
        blocks.append(f"{role.upper()}:\n{content}")
    return '\n\n'.join(blocks)


def _build_client(settings):
    client_kwargs = {'api_key': settings['api_key']}
    if settings.get('base_url'):
        client_kwargs['base_url'] = settings['base_url']
    return OpenAI(**client_kwargs)


def _create_deepseek_response(client, settings, messages, mode):
    reasoning_effort = 'high' if mode == 'force' else 'low'
    try:
        return client.chat.completions.create(
            model=settings['model'],
            messages=messages,
            stream=False,
            reasoning_effort=reasoning_effort,
            extra_body={'thinking': {'type': 'enabled'}},
            timeout=settings['timeout']
        )
    except Exception as exc:
        error_text = str(exc).lower()
        if not any(keyword in error_text for keyword in (
            'reasoning_effort', 'thinking', 'extra_body', 'unexpected', 'unknown parameter', 'invalid'
        )):
            raise

        return client.chat.completions.create(
            model=settings['model'],
            messages=messages,
            stream=False,
            timeout=settings['timeout']
        )


def _create_gpt_response(client, settings, messages, mode):
    max_tokens = settings['max_tokens_force'] if mode == 'force' else settings['max_tokens_auto']
    return client.responses.create(
        model=settings['model'],
        input=_build_response_input(messages),
        max_output_tokens=max_tokens,
        timeout=settings['timeout']
    )


def _extract_response_content(response, provider):
    if provider == 'deepseek':
        return response.choices[0].message.content
    return response.output_text


def _normalize_result(parsed_result, mode):
    if mode == 'force':
        analysis = str(parsed_result.get('analysis', '')).strip()
        return {'analysis': analysis}

    fingerprint = str(parsed_result.get('fingerprint', '')).strip()
    confidence = parsed_result.get('confidence', 0)
    evidence = parsed_result.get('evidence', [])
    if not isinstance(evidence, list):
        evidence = []
    return {
        'fingerprint': fingerprint,
        'confidence': confidence,
        'evidence': evidence[:3]
    }


def _normalize_text_result(content, mode):
    clean_text = _strip_json_text(content).strip()
    if mode == 'force':
        return {'analysis': clean_text[:80] if clean_text else '当前页面特征不足，建议人工复核'}

    first_line = clean_text.splitlines()[0].strip() if clean_text else ''
    fingerprint = first_line[:60] if first_line else 'unknown'
    return {'fingerprint': fingerprint, 'confidence': 0, 'evidence': []}


def analyze_page(evidence, mode='auto', provider=None, model=None):
    settings = _load_settings(provider=provider, model=model)
    if not settings['api_key']:
        return {'error': f"{settings['provider']} api key is not configured"}

    cache_key = _build_cache_key(mode, settings['provider'], settings['model'], evidence)
    if settings['cache_enabled']:
        cache_data = _load_cache()
        if cache_key in cache_data:
            cached_result = cache_data[cache_key]
            cached_result['cache_hit'] = True
            return cached_result

    try:
        messages = _build_messages(evidence, mode)
        client = _build_client(settings)
        if settings['provider'] == 'deepseek':
            raw_response = _create_deepseek_response(client, settings, messages, mode)
        else:
            raw_response = _create_gpt_response(client, settings, messages, mode)

        content = _extract_response_content(raw_response, settings['provider'])
        try:
            parsed_result = json.loads(_strip_json_text(content))
            final_result = _normalize_result(parsed_result, mode)
        except json.JSONDecodeError:
            final_result = _normalize_text_result(content, mode)
        final_result['cache_hit'] = False
        final_result['provider'] = settings['provider']
        final_result['model'] = settings['model']

        if settings['cache_enabled']:
            cache_data = _load_cache()
            cache_data[cache_key] = final_result
            _save_cache(cache_data)

        return final_result
    except Exception as exc:
        return {'error': str(exc)}
