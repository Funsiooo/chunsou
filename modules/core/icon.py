# -*- coding: utf-8 -*-

import requests
import base64
import mmh3
from urllib.parse import urljoin
import warnings
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from modules.core.agent import User_Agent  # 自定义模块，用于生成随机User-Agent

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
def get_ico_url(url, html_text=None):
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)  # 忽略证书告警

    try:
        html = html_text
        if html is None:
            response = requests.get(url, verify=False, timeout=5, headers=User_Agent())
            html = response.text

        if not html:
            return urljoin(url, "/favicon.ico")

        soup = BeautifulSoup(html, 'html.parser')

        def has_icon_rel(value):
            if not value:
                return False
            if isinstance(value, str):
                return 'icon' in value.lower()
            return 'icon' in ' '.join(value).lower()

        icon_link = soup.find('link', rel=has_icon_rel)

        if icon_link and icon_link.get('href'):
            return urljoin(url, icon_link['href'])
        return urljoin(url, "/favicon.ico")

    except requests.RequestException:
        return None
