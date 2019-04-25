#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created on 2018/3/22

import os
import requests
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

print "start download ..."

def hex2str(hex_data):
    hex_str = ''
    data_len = len(hex_data)
    print("data_len: ", data_len)
    for hex_x in hex_data:
        print("hex_x: ", hex_x)
        hex_x_str = chr(hex_x)
        print("hex_x_str: ", hex_x_str)
        hex_str = hex_str + hex_x_str
        print("hex_str: ", hex_str)
    return hex_str

def download(url):
    download_path = "download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    all_content = requests.get(url).text  # 获取M3U8的文件内容

    with open("index.m3u8", 'ab') as f:
        f.write(all_content)
        f.flush
    
    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的链接")

    file_line = all_content.split("\n")  # 读取文件里的每一行
    # print file_line
    # print "\n"
    # 通过判断文件头来确定是否是M3U8文件
    unknow = True  # 用来判断是否找到了下载的地址
    key = ""
    iv = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for index, line in enumerate(file_line):
        if '#' not in line:
            unknow = False
            # 拼出ts片段的URL
            pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index]
            res = requests.get(pd_url)
            c_fule_name = str(file_line[index])
            print c_fule_name
            if len(key):
                cryptor = AES.new(key, AES.MODE_CBC, iv)
            with open(download_path + "/" + c_fule_name, 'ab') as f:
                data_hex = cryptor.decrypt(res.content)
                print "data_hex len: ", len(data_hex)
                f.write(data_hex)
                f.flush()
        elif "#EXT-X-KEY" in line:
            method_pos = line.find("METHOD")
            comma_pos = line.find(",")
            method = line[method_pos:comma_pos].split('=')[1]

            uri_pos = line.find("URI")
            quotation_mark_pos = line.rfind('"')
            key_path = line[uri_pos:quotation_mark_pos].split('"')[1]
            print "key_path: ", key_path
            key_hex = requests.get(key_path).content
            print "key_hex: " , key_hex
            key = key_hex
            

    if unknow:
        raise BaseException("未找到对应的下载链接")
    else:
        print "下载完成"

if __name__ == '__main__':
    hls_url = sys.argv[1]
    download(hls_url)

