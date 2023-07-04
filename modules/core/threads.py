# -*- coding: utf-8 -*-

'''
@File    ：threads.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

from modules.core.args import argument


# 用于输入指定的线程数，默认为50
def num_threads():
    args = argument()
    if args.threads:
        num = args.threads
        return int(num)
    else:
        num = 50
        return int(num)
