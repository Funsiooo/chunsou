# -*- coding: utf-8 -*-

'''
@File    ：output.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

from modules.core.time import print_start_time,current_time
from modules.core.color import Colors
from modules.core.args import argument

def script_start():
    # 脚本启动时输出
    print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
          f"]{Colors.RESET} {Colors.GREEN}the identification results are as follows{Colors.RESET}")
    print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
          f"]{Colors.RESET} {Colors.GREEN}fingerprint recognition result order | Website fingerprint | Web title | "
          f"Web stack{Colors.RESET}")


def script_end():
    # 执行脚本结束提示语
    print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
          f"]{Colors.RESET} {Colors.YELLOW}{Colors.GREEN}the script has finished "
          f"executing, and the scan results are saved in the{Colors.RESET} {Colors.BROWN}{output_dir()}{Colors.RESET}"
          f" , {Colors.GREEN}scan end @ {current_time()}{Colors.RESET}")


def output_dir():
    args = argument()
    if args.output:
        out_file = args.output
        output_dir = out_file
        return output_dir
    else:
        out_file = 'results/results.txt'
        output_dir = out_file
        return output_dir


def fofa_output_dir():
    args = argument()
    if args.output:
        out_file = args.output
        return out_file
    else:
        out_file = 'results/fofa.txt'
        return out_file


def fofa_start():
    # 脚本启动时输出
    print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
          f"]{Colors.RESET} {Colors.GREEN}Starting invoke fofa api results are as follows{Colors.RESET}")
    print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
          f"]{Colors.RESET} {Colors.GREEN}you can in the /config/config.ini to adjust result quantity"
          f"Web stack{Colors.RESET}")


def fofa_end():
    # 执行脚本结束提示语
    print(f"{Colors.CYAN}{print_start_time()} {Colors.GREEN}[*]{Colors.RESET} {Colors.GREEN}[INFO"
          f"]{Colors.RESET} {Colors.YELLOW}{Colors.GREEN}the script has finished "
          f"executing, and the scan results are saved in the{Colors.RESET} {Colors.BROWN}{fofa_output_dir()}{Colors.RESET}"
          f" , {Colors.GREEN}scan end @ {current_time()}{Colors.RESET}")

