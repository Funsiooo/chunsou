# -*- coding: utf-8 -*-

import requests
import base64
import mmh3
from urllib.parse import urljoin
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
from modules.core.agent import User_Agent

def get_hash(content):
    def mmh3_hash32(raw_bytes, is_uint32=True):
        h32 = mmh3.hash(raw_bytes)

        if is_uint32:
            return str(h32 & 0xffffffff)
        else:
            return str(h32)

    def stand_base64(braw) -> bytes:
        bckd = base64.standard_b64encode(braw)
        buffer = bytearray()
        for i, ch in enumerate(bckd):
            buffer.append(ch)
            if (i + 1) % 76 == 0:
                buffer.append(ord('\n'))
        buffer.append(ord('\n'))
        return bytes(buffer)

    return mmh3_hash32(stand_base64(content))

def get_ico_url(url):
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)
    headers = User_Agent()
    try:

        response = requests.get(url, verify=False, timeout=3, headers=headers)
        html = response.text

        icon_index = html.find("<link rel=\"icon\"")
        shortcut_index = html.find("<link rel=\"shortcut icon\"")

        if icon_index == -1 or shortcut_index == -1:
            favicon_url = urljoin(url, "/favicon.ico")
            return favicon_url

        if icon_index != -1:
            end_index = html.find(">", icon_index)
            link_tag = html[icon_index:end_index]
            favicon_path = link_tag.split('href="')[1].split('"')[0]

        else:
            end_index = html.find(">", shortcut_index)
            link_tag = html[shortcut_index:end_index]
            favicon_path = link_tag.split('href="')[1].split('"')[0]

        if favicon_path.endswith("favicon.ico"):
            favicon_url = urljoin(url, favicon_path)
            return favicon_url


    except requests.exceptions.RequestException:
        return None
