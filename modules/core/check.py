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
        current_version = '1.6'

        print(f"[{Colors.CYAN}{print_start_time()}{Colors.RESET}] [{Colors.GREEN}*{Colors.RESET}] [{Colors.GREEN}INFO"
              f"{Colors.RESET}] {Colors.GREEN}checking for the latest version{Colors.RESET}")

        url = "https://github.com/Funsiooo/chunsou/blob/main/version"
        warnings.filterwarnings('ignore', category=InsecureRequestWarning)

        headers = User_Agent()

        response = requests.get(url, headers=headers, timeout=3, verify=False, proxies=proxies(), allow_redirects=False)

        html = response.text

        pattern = r'(?<="blob":{"rawLines":\[").*?(?=\"],"stylingDirectives":\[)'

        match = re.search(pattern, html)

        version = match.group()


        if version == current_version:
            print(f"[{Colors.CYAN}{print_start_time()}{Colors.RESET}] [{Colors.GREEN}*{Colors.RESET}] [{Colors.GREEN}INFO"
                  f"{Colors.RESET}] {Colors.GREEN}the current version is the latest version{Colors.RESET}")
        elif version != current_version:
            print(f"[{Colors.CYAN}{print_start_time()}{Colors.RESET}] [{Colors.GREEN}*{Colors.RESET}] [{Colors.GREEN}INFO"
                  f"{Colors.RESET}] {Colors.GREEN}the current version is not the latest version{Colors.RESET}")
        else:
            print(f"[{Colors.CYAN}{print_start_time()}{Colors.RESET}] [{Colors.GREEN}*{Colors.RESET}] [{Colors.GREEN}INFO"
                  f"{Colors.RESET}] {Colors.GREEN}check failed, please visit the repository to check for yourself{Colors.RESET}")

    except Exception as e:
        print(f"[{Colors.CYAN}{print_start_time()}{Colors.RESET}] [{Colors.GREEN}*{Colors.RESET}] [{Colors.GREEN}INFO"
              f"{Colors.RESET}] {Colors.GREEN}check failed, please visit the repository to check for yourself{Colors.RESET}")

