# -*- coding: utf-8 -*-

'''
@File    ：time.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

import datetime
from modules.core.color import Colors

# 记录脚本执行初始时间
def print_start_time():
    start_time = datetime.datetime.now()
    time = start_time.strftime("%H:%M:%S")
    return time


# 记录脚本执行结束时间
def print_end_time():
    end_time = datetime.datetime.now()
    time = end_time.strftime("%H:%M:%S")
    print(f"{Colors.GREEN}[+]{Colors.RESET} {Colors.GREEN}[{time}]{Colors.RESET} {Colors.GREEN} The script execution "
          f"has finished Hopefully it has found what you are looking for {Colors.RESET}")


# 获取当前时间，用于记录用户的输出时间
def current_time():
    current_datetime = datetime.datetime.now()
    return current_datetime
