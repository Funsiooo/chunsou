# -*- coding: utf-8 -*-

'''
@File    ：check.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
from modules.core.agent import User_Agent
from modules.core.proxy import proxies
import re
from modules.core.time import print_start_time,current_time
from modules.core.color import Colors

def check_version():
    try:
        current_version = 'v1.7'

        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}*{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO"
              f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}Checking for latest version{Colors.RESET}")

        url = "https://github.com/Funsiooo/chunsou/blob/main/version"
        warnings.filterwarnings('ignore', category=InsecureRequestWarning)

        headers = User_Agent()

        response = requests.get(url, headers=headers, timeout=3, verify=False, proxies=proxies(), allow_redirects=False)

        html = response.text

        pattern = r'(?<="blob":{"rawLines":\[").*?(?=\"],"stylingDirectives":\[)'

        match = re.search(pattern, html)

        version = match.group()


        if version == current_version:
            print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}*{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO"
                  f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}Current version {Colors.GREEN}({current_version}){Colors.RESET} {Colors.WHITE}is the latest{Colors.RESET}")
        elif version != current_version:
            print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}*{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO"
                  f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}Current version{Colors.RESET} {Colors.GREEN}({current_version}){Colors.RESET} {Colors.WHITE}is not the latest{Colors.RESET}")
        else:
            print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}*{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO"
                  f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}Check failed. Verify in the repository.{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.WHITE}[{Colors.RESET}{Colors.CYAN}{print_start_time()}{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.GREEN}*{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}[{Colors.RESET}{Colors.CYAN}INFO"
              f"{Colors.RESET}{Colors.WHITE}]{Colors.RESET} {Colors.WHITE}Check failed. Verify in the repository.{Colors.RESET}")

