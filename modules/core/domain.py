# -*- coding: utf-8 -*-

'''
@File    ：domain.py
@IDE     ：PyCharm
@Author  ：Funsiooo
@Github  ：https://github.com/Funsiooo
'''

import subprocess
import csv
import os
from modules.core.args import argument


'''
single_subdomains
'''
def oneforall():
    script_path = 'modules/plugins/OneForAll/oneforall.py'
    return script_path


def single_output_file_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = 'results'
    parent_dir = os.path.dirname(script_dir)
    save_path = os.path.join(parent_dir, os.path.pardir, save_dir, 'subdomains.csv')
    return save_path


# 处理将结果保存为txt
def single_output_file_txt():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = 'results'
    parent_dir = os.path.dirname(script_dir)
    save_path = os.path.join(parent_dir, os.path.pardir, save_dir, 'subdomains.txt')
    return save_path


def single_extract_column(single_csv_file, single_column_index, single_output_file):
    with open(single_csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        column_data = [row[single_column_index] for row in reader]

    with open(single_output_file, 'w') as file:
        for item in column_data:
            file.write(item + '\n')


def single_csv_to_txt():
    single_csv_file = single_output_file_csv()
    single_column_index = 4  # 替换为你要提取的列的索引（从0开始）
    single_output_file = single_output_file_txt()  # 替换为输出文件的路径

    single_extract_column(single_csv_file, single_column_index, single_output_file)


def subdomain_single():
    args = argument()
    domain = args.domain

    subprocess.run(['python3', oneforall(), '--target', domain,
                    '--path', single_output_file_csv(), 'run'])

    single_csv_to_txt()


'''
List_subdomains
'''
def lists_output_file_csv():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    save_dir = 'results'

    parent_dir = os.path.dirname(script_dir)
    save_path = os.path.join(parent_dir, os.path.pardir, save_dir, 'subdomains.csv')
    return save_path


def lists_extract_column(lists_csv_file, lists_column_index, lists_output_file):
    with open(lists_csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        column_data = [row[lists_column_index] for row in reader]

    with open(lists_output_file, 'w') as file:
        for item in column_data:
            # 添加 “http://” 和 “https://”
            http_item = 'http://' + item
            https_item = 'https://' + item
            file.write(http_item + '\n')
            file.write(https_item + '\n')


def lists_output_file_txt():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = 'results'
    parent_dir = os.path.dirname(script_dir)
    save_path = os.path.join(parent_dir, os.path.pardir, save_dir, 'subdomains.txt')
    return save_path


def lists_csv_to_txt():
    lists_csv_file = lists_output_file_csv()
    lists_column_index = 0  # 替换为你要提取的列的索引（从0开始）
    lists_output_file = lists_output_file_txt()  # 替换为输出文件的路径

    lists_extract_column(lists_csv_file, lists_column_index, lists_output_file)


def subdomain_list():
    args = argument()
    domain = args.domains
    subprocess.run(['python3', oneforall(), '--targets', domain,
                    '--path', lists_output_file_csv(), 'run'])

    lists_csv_to_txt()



