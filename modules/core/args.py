# -*- coding: utf-8 -*-

'''
@File    ：args.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''


import argparse
from.color import Colors

def argument():
    parser = argparse.ArgumentParser(usage="python3 chunsou.py [options]", add_help=False)
    target = parser.add_argument_group("target")
    target.add_argument('-u', '--url', metavar='', help='scan for a single url')
    target.add_argument('-f', '--file', metavar='', help='specify a file for multi scanning')

    subdomain = parser.add_argument_group("subdomain")
    subdomain.add_argument('-du', '--domain', metavar='', help='subdomain blasting of a single domain name')
    subdomain.add_argument('-df', '--domains', metavar='', help='subburst the domain name in the specified file')

    api = parser.add_argument_group("api")
    api.add_argument('-fo', '--fofa', metavar='', help='call the fofa api for asset collection')
    api.add_argument('-hu', '--hunter', metavar='', help='call the hunter api for asset collection')
    api.add_argument('-tip', action='store_true', help='spatial mapping search syntax reference')

    others = parser.add_argument_group("others")
    others.add_argument('-p', '--proxy', metavar='', help='proxy scan traffic')
    others.add_argument('-t', '--threads', metavar='', help='specify the number of scanning threads, default 50')
    others.add_argument('-h', '--help', action="help", help="show this help message and exit")
    others.add_argument('-o', '--output',metavar='', help='specified output file')
    others.add_argument('-e', action='store_true', help='displays the specific error cause that cannot be identified by multi-object scanning')
    

    example = parser.add_argument_group("example")
    example.add_argument(action='store_false', dest="-u , --url            python3 chunsou.py -u 'http://example.com'\n  "
                                                    "-f , --file           python3 chunsou.py -f urls.txt\n  "
                                                    "-p  , --proxy         python3 chunsou.py -u http://example.com -p http://127.0.0.1\n  "
                                                    "-t  , --threads       python3 chunsou.py -f urls.txt -t 100\n  "
                                                    "-o  , --output        python3 chunsou.py -f -o results.xlsx\n  "        
                                                    "-du , --domain        python3 chunsou.py -du example.com\n  "
                                                    "-df , --domains       python3 chunsou.py -df domains.txt\n  "
                                                    "-fo , --fofa          python3 chunsou.py -fo domain=\"example.com\"\n  "
                                                    "-hu , --hunter        python3 chunsou.py -hu domain=\"example.com\"\n  "
                                                    "-e  ,                 python3 chunsou.py -f urls.txt -e\n  "
                                                    "-tip,                 python3 chunsou.py -tip"  )

    return parser.parse_args()
