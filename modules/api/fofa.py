# -*- coding: utf-8 -*-

'''
@File    ：fofa.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

'''
FOFA_API 接口：https://fofa.info/api/v1/search/all?email=fofa_邮箱&key=fofa_key&qbase64
=需要查询的语法base64编码&page=查询的页数&size=9999查询显示的数量

前端搜索规则：https://fofa.info/result?qbase64=ZG9tYWluPSJiYWlkdS5jb20i&page=2&page_size=10

API接口规则：
1. 普通用户API扣费规则：
一次请求/1F币，每次请求最多10000条。

2. 会员API扣费规则：
•  普通会员前100条免费，高级会员前10000条免费。可以分多次请求获取。
•  超出免费的部分后：一次请求/1F币，每次请求最多10000条。

所以，避免多扣F币的方式为：size设置为10000，每页取10000条。

api支持获取的字段：host, title, ip, domain, port, country, province, city, country_name, header, server, protocol, banner, cert, isp, as_number, as_organization, latitude, longitude, lastupdatetime等。

图标查询语法：
icon_hash=""
'''

import requests
import base64
import configparser
import sys
from modules.core.color import Colors
from modules.core.time import print_start_time
from modules.core.args import argument
from modules.core.output import script_end,fofa_output_dir,fofa_end,fofa_start


def base64_encode(string):
    string_bytes = string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    return base64_bytes


def fofa_search(email,key,qbase64,page,size):
    api = "https://fofa.info/api/v1/search/all"

    params = {
        'email':email,
        'key':key,
        'qbase64':qbase64,
        'page':page,
        'size':size
    }

    try:
        res = requests.get(url=api,data=params)
        res.raise_for_status()
        response = res.json()
        return response['results']


    except requests.exceptions.RequestException as e:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.RED}[-]{Colors.RESET} {Colors.GREEN}[INFO"
              f"]{Colors.RESET}  {Colors.RED}{str(e)}{Colors.RESET}\n")
        sys.exit()


def fofa_main():
    args = argument()
    out_file = fofa_output_dir()

    fofa_query_base64 = base64_encode(args.fofa)

    fofa_page = 1


    config = configparser.ConfigParser()
    config.read('modules/config/config.ini')

    fofa_email = config.get('fofa_email', 'email').strip('"')

    fofa_key = config.get('fofa_api_key', 'key').strip('"')

    fofa_size = config.get('size', 'size').strip('"')

    if not fofa_email or not fofa_key or not fofa_key:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
              f"]{Colors.RESET} {Colors.GREEN}Starting invoke fofa api results are as follows{Colors.RESET}")
        print(f"{Colors.CYAN}{print_start_time()} {Colors.RED}[-]{Colors.RESET} {Colors.GREEN}{Colors.RESET}"
              f"{Colors.RED}Fofa invoke failure , Please Check that the fofa api file config.ini is configured "
              f"correctly"
              f".{Colors.RESET}")

    results = fofa_search(fofa_email,fofa_key,fofa_query_base64,fofa_page,fofa_size)

    fofa_start()


    try:
        with open(out_file, 'w') as file:
            for result in results:

                print(f"{Colors.CYAN}{print_start_time()}{Colors.RESET} {Colors.GREEN}[+]{Colors.RESET} {Colors.YELLOW}{result[0]}{Colors.RESET}")

                if not result[0].startswith('http://') and not result[0].startswith('https://'):
                    http_result = 'http://' + result[0]
                    https_result = 'https://' + result[0]

                    file.write(http_result + '\n')
                    file.write(https_result + '\n')

            fofa_end()


    except Exception as e:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.RED}[-]{Colors.RESET} {Colors.GREEN}[INFO"
              f"]{Colors.RESET} fofa invoke fail, please check your network or fofa syntax" + str(e))