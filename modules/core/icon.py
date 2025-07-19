# -*- coding: utf-8 -*-

import requests
import base64
import mmh3
from urllib.parse import urljoin
import warnings
from urllib3.exceptions import InsecureRequestWarning
from modules.core.agent import User_Agent  # 自定义模块，用于生成随机User-Agent
from modules.core.color import Colors
from modules.core.time import print_start_time

# 计算 favicon 内容的 mmh3 哈希值，用于指纹识别
def get_hash(content):
    # 内部函数：使用 mmh3 进行 hash32 计算
    def mmh3_hash32(raw_bytes, is_uint32=True):
        h32 = mmh3.hash(raw_bytes)
        if is_uint32:
            return str(h32 & 0xffffffff)  # 保证返回正整数
        else:
            return str(h32)

    # 对原始内容进行标准 base64 编码，并在每76个字符处换行
    def stand_base64(braw) -> bytes:
        bckd = base64.standard_b64encode(braw)
        buffer = bytearray()
        for i, ch in enumerate(bckd):
            buffer.append(ch)
            if (i + 1) % 76 == 0:
                buffer.append(ord('\n'))
        buffer.append(ord('\n'))
        return bytes(buffer)

    # 返回计算出的哈希值
    return mmh3_hash32(stand_base64(content))


# 获取目标网站 favicon 的 URL 地址
def get_ico_url(url):
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)  # 忽略证书告警
    headers = User_Agent()  # 使用自定义的 User-Agent

    try:
        # 发送请求，获取 HTML 内容
        response = requests.get(url, verify=False, timeout=3, headers=headers)
        html = response.text

        # 查找页面中 <link rel="icon"> 或 <link rel="shortcut icon"> 标签
        icon_index = html.find("<link rel=\"icon\"")
        shortcut_index = html.find("<link rel=\"shortcut icon\"")

        # 如果两个都找不到，默认使用 /favicon.ico 路径
        if icon_index == -1 and shortcut_index == -1:
            return urljoin(url, "/favicon.ico")

        # 如果找到了 rel="icon"，优先使用
        if icon_index != -1:
            end_index = html.find(">", icon_index)
            link_tag = html[icon_index:end_index]
        else:
            # 否则使用 rel="shortcut icon"
            end_index = html.find(">", shortcut_index)
            link_tag = html[shortcut_index:end_index]

        # 提取 href 路径
        if 'href="' in link_tag:
            favicon_path = link_tag.split('href="')[1].split('"')[0]
            # 拼接成完整 URL 并返回
            return urljoin(url, favicon_path)
        else:
            # 没有 href 字段时，使用默认路径
            return urljoin(url, "/favicon.ico")

    except requests.exceptions.RequestException as e:
        # 捕获网络异常并返回 None
        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}{status_code}"
          f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.YELLOW_B}{url}{Colors.RESET} {Colors.RED}ERROR: {e}{Colors.RESET}")
        return None
