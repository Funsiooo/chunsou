# -*- coding: utf-8 -*-

'''
@File    ：hunter.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

import requests
import base64
import json

from modules.core.args import argument
# 导入hunter输出结果函数
from modules.core.output import hunter_save_to_excel,hunter_start,hunter_end,hunter_output_dir
from modules.core.color import Colors
from modules.core.time import print_start_time
# 读取 config.ini 的参数
import configparser
from modules.core.agent import User_Agent

def base64_encode(string):
    query_sentence = string
    # hunter 搜索语句加密
    search = base64.urlsafe_b64encode(query_sentence.encode("utf-8"))
    search_result = str(search, 'utf8')
    return search_result

# 定义一个fofa_search函数
def hunter_search(qbase64):
    # 创建ConfigParser对象并读取config.ini文件
    config = configparser.ConfigParser()
    config.read('modules/config/config.ini')

    # 获取Section1中的param1的值
    hunter_api_key = config.get('hunter_api_key', 'key').strip('"')

    # 获取Section1中的param2的值，并将其解析为整数
    hunter_size = config.get('hunter_size', 'size').strip('"')

    if not hunter_api_key or not hunter_size:
        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.RED}-{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.RED}hunter invoke failure , Please Check that the hunter api file config.ini is configured correctly{Colors.RESET}")


    # api_key = ''
    page = '1'
    # page_size = '10'
    is_web = '3'

    # api 接口地址
    api = 'https://hunter.qianxin.com/openApi/search?api-key='+ str(hunter_api_key) + '&search='+ str(qbase64) + '&page=' + str(page) + '&page_size=' + str(hunter_size) + '&is_web=' + str(is_web)
    res = requests.get(url=api, headers = User_Agent())
    # results 为调用 hunter 后获取到的原始 json 结果
    results = json.loads((res.content).decode('utf-8'))

    # 创建一个列表用于存放各字段，稍后返回该值，待被调用写入excel
    params_list = []
    # for 循环获取 results 结果的 data 中的 arr 中的 json 数据
    for i in range(len(results["data"]["arr"])):
        # 以下为 hunter 的调用结果，例：is_risk = results内容中的 data -》 arr -》[i](循环) -》is_risk 的json字段数值，i为不断循环获取 is_risk 的值
        is_risk = results["data"]["arr"][i]["is_risk"]  # 是否危险
        url = results["data"]["arr"][i]["url"]  # 网站链接
        ip = results["data"]["arr"][i]["ip"]    # IP地址
        port = results["data"]["arr"][i]["port"]    # 端口
        web_title = results["data"]["arr"][i]["web_title"]  # 网站标题
        domain = results["data"]["arr"][i]["domain"]    # 域名
        is_risk_protocol = results["data"]["arr"][i]["is_risk_protocol"]    # 是否危险协议
        protocol = results["data"]["arr"][i]["protocol"]    # 协议
        base_protocol = results["data"]["arr"][i]["base_protocol"]  # 基础协议
        status_code = results["data"]["arr"][i]["status_code"]  # 状态码

        os = results["data"]["arr"][i]["os"]
        company = results["data"]["arr"][i]["company"]
        number = results["data"]["arr"][i]["number"]
        country = results["data"]["arr"][i]["country"]
        city = results["data"]["arr"][i]["city"]

        # 将各字段赋值给 params，然后存放在 params_list 中,然后我们就可以 return params_list,待其他函数调用即可
        params = {
            # "is_risk": is_risk,
            "url": url,
            "ip": ip,
            "port": port,
            "web_title": web_title,
            "domain": domain,
            # "is_risk_protocol": is_risk_protocol,
            "status_code": status_code,
            "protocol": protocol,
            "base_protocol": base_protocol,
            "os": os,
            "company": company,
            "number": number,
            "country": country,
            "city": city,
        }

        if results["data"]["arr"][i]["component"] is not None:
            for j in range(len(results["data"]["arr"][i]["component"])):
                name = results["data"]["arr"][i]["component"][j]["name"]
                version = results["data"]["arr"][i]["component"][j]["version"]
                component = create_component(name, version)

                # 将 component 更新 params 字典
                params.update(component)


        params_list.append(params)

        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}+{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO"
          f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {url}")
        

        # print(url,ip,port,web_title,domain,is_risk_protocol,is_risk,protocol,base_protocol,status_code,os,company,number,country,city)


    return params_list



def create_component(name, version):
    return {"name": name, "version": version}


def hunter_main():
    args = argument()

    # 执行脚本开始提示语
    hunter_start()
    hunter_query_base64 = base64_encode(args.hunter)

    # 获取上面的请求结果
    results = hunter_search(hunter_query_base64)

    # 调用生成 excel 文件
    hunter_save_to_excel(list(results))

    # 执行脚本结束提示语
    hunter_end()

