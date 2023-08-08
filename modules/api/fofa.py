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
# 读取 config.ini 的参数
import configparser

# 用于终止程序
import sys
from modules.core.color import Colors
from modules.core.time import print_start_time
from modules.core.args import argument
from modules.core.output import script_end,fofa_output_dir,fofa_end,fofa_start

from modules.core.output import fofa_save_to_excel

import sys
import csv
# 用于获取协议
from urllib.parse import urlparse
import argparse
# 处理变为 xlsx 文件
from openpyxl import Workbook
# 删除生成的csv 文件
import os
# 标题背景颜色、修改字体样式、边框
from openpyxl.styles import Font, PatternFill,Border, Side

def base64_encode(string):
    # 先将 string 确认编码为 'utf-8'
    string_bytes = string.encode('utf-8')
    # 然后通过 base64 模块编码 string_bytes 为base64
    base64_bytes = base64.b64encode(string_bytes)
    # 返回 base64_bytes
    return base64_bytes

# 定义一个fofa_search函数
def fofa_search(email,key,qbase64,page,size,fields):
    # api 接口
    api = "https://fofa.info/api/v1/search/all"

    # api 接口的请求参数，若没有该参数无法正常进行 fofa api 调用
    params = {
        'email':email,
        'key':key,
        'qbase64':qbase64,
        'page':page,
        'size':size,
        'fields': fields
    }

    try:
        res = requests.get(url=api,data=params)
        res.raise_for_status()
        response = res.json()
        # 返回获取的值保存到 response 键值
        return response['results']


    except requests.exceptions.RequestException as e:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.RED}[-]{Colors.RESET} {Colors.GREEN}[INFO"
              f"]{Colors.RESET}  {Colors.RED}{str(e)}{Colors.RESET}\n")
        sys.exit()


def fofa_main():
    # 引入 argument() 函数实现参数化输入
    args = argument()

    # 这一步骤比较重要，为 chunsou.py 调用需要正确编写的一步骤
    fofa_query_base64 = base64_encode(args.fofa)
    # original_string = '''domain="baidu.com"'''
    #fofa_query_base64 = base64_encode(original_string)

    fofa_page = 1

    # 定义调用fofa输出的api信息
    fofa_fields = 'host,title,domain,link,ip,port,base_protocol,server'


    # 创建ConfigParser对象并读取config.ini文件
    config = configparser.ConfigParser()
    config.read('modules/config/config.ini')

    # 获取Section1中的param1的值
    fofa_email = config.get('fofa_email', 'email').strip('"')

    # 获取Section1中的param2的值，并将其解析为整数
    fofa_key = config.get('fofa_api_key', 'key').strip('"')

    # 获取Section2中的param4的值
    fofa_size = config.get('fofa_size', 'size').strip('"')

    if not fofa_email or not fofa_key or not fofa_key:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
              f"]{Colors.RESET} {Colors.GREEN}Starting invoke fofa api results are as follows{Colors.RESET}")
        print(f"{Colors.CYAN}{print_start_time()} {Colors.RED}[-]{Colors.RESET} {Colors.GREEN}{Colors.RESET}"
              f"{Colors.RED}Fofa invoke failure , Please Check that the fofa api file config.ini is configured "
              f"correctly"
              f".{Colors.RESET}")

    results = fofa_search(fofa_email,fofa_key,fofa_query_base64,fofa_page,fofa_size,fofa_fields)

    # 执行脚本开始提示语
    fofa_start()

    #遍历 results 的结果保存至 result 中
    for result in results:
        # 先在终端打印 fofa 获取的结果
        fofa_results_url = result[0]
        # fofa_results_title = result[1]
        # if fofa_results_title == '':
        #     fofa_results_title = 'None'
        print(f"{Colors.CYAN}{print_start_time()}{Colors.RESET} {Colors.GREEN}[+]{Colors.RESET} {fofa_results_url}")

    # 执行脚本结束提示语
    fofa_end()

    # 将fofa 调用 api 的结果保存到 excel 中去
    fofa_save_to_excel(results)

