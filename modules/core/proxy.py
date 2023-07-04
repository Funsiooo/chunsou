# -*- coding: utf-8 -*-

'''
@File    ：proxy.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

from modules.core.args import argument


def proxies():
    args = argument()
    if args.proxy:
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
        return proxies
    else:
        proxies = None
        return proxies