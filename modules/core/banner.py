# -*- coding: utf-8 -*-

'''
@File    ：banner.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

from modules.core.time import current_time

def banner():
    ORANGE = '\033[01;38;2;252;166;82m'
    RESET = '\033[0m'

    banner = r'''
       _                                      
      | |                                     
  ___ | |__   _   _  _ __   ___   ___   _   _ 
 / __|| '_ \ | | | || '_ \ / __| / _ \ | | | |
| (__ | | | || |_| || | | |\__ \| (_) || |_| |
 \___||_| |_| \__,_||_| |_||___/ \___/  \__,_|                    
    https://github.com/Funsiooo  By Funsiooo 
    '''

    currrent_time = f" [*] Starting @ {current_time()}\n"
    color_banner = ORANGE + banner + RESET
    print(color_banner)
    print(currrent_time)

def banner_2():
    ORANGE = '\033[01;38;2;252;166;82m'
    RESET = '\033[0m'
    banner = f'''
      ______                                    
_________  /_____  _________________________  __
_  ___/_  __ \  / / /_  __ \_  ___/  __ \  / / /
/ /__ _  / / / /_/ /_  / / /(__  )/ /_/ / /_/ / 
\___/ /_/ /_/\__,_/ /_/ /_//____/ \____/\__,_/  v 1.5               
    http://github.com/Funsiooo By Funsiooo
    '''

    currrent_time = f" [*] Starting @ {current_time()}\n"
    color_banner = ORANGE + banner + RESET
    print(color_banner)
    print(currrent_time)

