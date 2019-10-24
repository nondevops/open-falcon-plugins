#!/usr/bin/env python
#-*- coding:utf-8 -*-

# rquire: python3 urllib3 pyopenssl

'''
# 问题1:
2019/10/24 11:03:28 scheduler.go:119: debug %s(%s) running.../opt/open-falcon-agent/plugin/cert/60_check_ssl_expire_time.py
2019/10/24 11:03:28 scheduler.go:136: error [ERROR] plugin start fail: %s(%s) , error: %s
/opt/open-falcon-agent/plugin/cert/60_check_ssl_expire_time.pyfork/exec /opt/open-falcon-agent/plugin/cert/60_check_ssl_expire_time.py: exec format error

问题1解决:
脚本必须要加解释器"#!/usr/bin/env python"


# 问题2:
2019/10/24 11:12:17 scheduler.go:175: debug [DEBUG] stdout of/opt/open-falcon-agent/plugin/cert/60_check_ssl_expire_time.py()is blank

问题2解决:


'''

from urllib3.contrib import pyopenssl
from datetime import datetime
from sys import argv

import os,sys
import socket
import time
import json

domain_list = [
'baidu.com',
'zbj.com',
'chatm.com',
'www.chinazhyc.com',
'kubanquan.com',
'op.zhubajie.la',
'open.kubanquan.com',
'token.kubanquan.com',
'www.kubanquan.com',
'as.zbjimg.com']

timestamp = int(time.time())
step = 60
counterType = "GAUGE"

class CheckSSL():

    def __init__(self, url):
        self.url = url
        self.hostname = self.read_endpoint_value()


    def read_endpoint_value(self):
        try:
            with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
                load_dict = json.load(f)
                return load_dict["hostname"]

        except OSError:
            pass

    def get_str_time(self):
        x509 = pyopenssl.OpenSSL.crypto.load_certificate(pyopenssl.OpenSSL.crypto.FILETYPE_PEM,
                                                         pyopenssl.ssl.get_server_certificate((self.url, 443)))
        data = x509.get_notAfter().decode()[0:-1]
        return data

    def get_ssl_time(self):
        ssl_timestamp = int(time.mktime(time.strptime(self.get_str_time(), '%Y%m%d%H%M%S')))
        now_timestamp = time.time()
        time_s = (ssl_timestamp - now_timestamp)
        time_d = (time_s / 3600 / 24)
        time_d_int = int(time_d)
        return time_d_int

    def create_record(self):
        t = {}
        t['endpoint'] = self.hostname
        t['timestamp'] = timestamp
        t['step'] = step
        t['counterType'] = counterType
        t['metric'] = 'ssl.cert.status'
        t['value'] = self.get_ssl_time()
        t['tag'] = self.url
        return t


if __name__ == "__main__":
    #url = argv[1]
    data = []
    for dn in domain_list:
        #print(dn)
        a = CheckSSL(dn)
        d = a.create_record()
        data.append(d)
    print(json.dumps(data))