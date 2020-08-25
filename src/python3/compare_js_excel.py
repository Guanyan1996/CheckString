#!/usr/bin/env python3
""" 
 -*- coding: utf-8 -*-
 @Time    : 2020/8/25 15:15
 @Author  : yguan
 @Site    : 
 @File    : compare_js_excel.py
 @Software: PyCharm
"""
import json
import re
import xlrd
from collections import defaultdict
import csv
import os
import datetime
import shutil


def del_java_note(text: str) -> str:
    """
    删除 java 注释 /* */：
    /\*{1,2}[\s\S]*?\*/
    删除 java 注释 //：
    //[\s\S]*?\n
    删除xml注释：
    <!-[\s\S]*?-->
    删除空白行：
    ^\s*\n
    :return: str
    """
    text1 = re.sub(r'/\*{1,2}[\s\S]*?\*/', "\n", text)
    text2 = re.sub(r"//[\s\S]*?\n", "\n", text1)
    text3 = re.sub(r'^\s*\n', "", text2)
    return text3


def js_text_find_json(file):
    text = file.read()
    return json.loads(del_java_note(text[text.find('{'):text.rfind('}') + 1]))


def read_xlsx(filepath):
    return xlrd.open_workbook(filepath)


def compare_js_excel(js_filepath, excel_filepath, compare_excel_row_name, suffix="", outputfilepath="."):
    outputfilepath = os.path.join(outputfilepath, suffix)
    os.makedirs(outputfilepath, exist_ok=True)
    shutil.copy(js_filepath, outputfilepath)
    shutil.copy(excel_filepath, outputfilepath)
    outputfile = open(
        os.path.join(outputfilepath,
                     f"{os.path.splitext(os.path.basename(js_filepath))[0]}_compare.csv"), "w",
        encoding="utf-8-sig")
    write = csv.writer(outputfile, dialect='excel', )
    header = ["key", "value", "match"]
    write.writerow(header)

    compare_js_dict = js_text_find_json(open(js_filepath, "r"))
    compare_excel_dict = defaultdict(str)
    excel_data = read_xlsx(excel_filepath).sheet_by_index(0)
    language_data = excel_data.col_values(
        excel_data.row_values(0, start_colx=0, end_colx=None).index(compare_excel_row_name))
    for key, value in zip(excel_data.col_values(0), language_data):
        compare_excel_dict[key] = value
    for key, value in compare_js_dict.items():
        if compare_excel_dict[key] == value:
            row = [key, value, True]
        else:
            row = [key, value, False]
        write.writerow(row)
    print(f"{js_filepath} | vs | {excel_filepath}: 对比完成 --> {outputfile}")


def run(info_file):
    suffix = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    for index in range(xlrd.open_workbook(info_file).sheet_by_index(0).nrows):
        data = xlrd.open_workbook(info_file).sheet_by_index(0).row_values(index)
        compare_js_excel(data[0], data[1], data[2], suffix)


if __name__ == '__main__':
    run("mapping.xlsx")
