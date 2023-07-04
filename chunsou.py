# -*- coding: utf-8 -*-

'''
@File    ：chunsou.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

from modules.core.banner import banner,banner_2
from modules.core.args import argument
from modules.core.domain import subdomain_single,subdomain_list
from modules.api.fofa import fofa_main
from modules.core.scan import lists_main,single_main
from modules.core.color import Colors
from modules.core.time import print_start_time


def main():
    args = argument()

    try:
        if args.url:
            single_main()

        if args.file:
            lists_main(args.file)


        if args.domain:
            subdomain_single()

        if args.domains:
            subdomain_list()

        if args.fofa:
            fofa_main()

    except Exception as e:
        print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}{Colors.RED}[-] Error occurred , Check whether the "
              f"network, command, or configuration is correct.")


if __name__ == '__main__':
    banner_2()
    main()
