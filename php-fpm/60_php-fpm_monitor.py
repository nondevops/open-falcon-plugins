#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
python的requests模块需要额外安装，故这里使用urllib2模块完成http请求
'''

import time
import urllib2
import json
import os
import re

def pushFalcon(endpoint, metric, value, tag, counterType="GAUGE"):
    '''
    封装传递数据给falcon agent的接口
    '''
    ts = int(time.time())
    payload = [
    {
        "endpoint": endpoint,
        "metric": metric,
        "timestamp": ts,
        "step": 60,
        "value": value,
        "counterType": counterType,
        "tags": tag,
    },
    ]
    request = urllib2.Request('http://127.0.0.1:11988/v1/push', data=json.dumps(payload))
    response = urllib2.urlopen(request, timeout=1)
    return response.read()


def getStatus():
    '''
    获取php-fpm的状态，并以json格式输出
    '''
    host = {'Host': 'localhost'}
    request = urllib2.Request('http://127.0.0.1/status?json', headers=host)
    response = urllib2.urlopen(request, timeout=1)
    return response.read()


def getIp():
    '''
    获取本机ip地址
    '''
    ip_addr = os.popen('/sbin/ip addr show dev bond0').read()
    ip = re.search(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)', ip_addr).group()
    return ip


if __name__ == '__main__':
    phpStatus = json.loads(getStatus())
    endpoint = getIp()
    tag = "from=" + endpoint
    # POST数据到falcon agent
    pushFalcon(endpoint, 'php_conn_per_s', phpStatus['accepted conn'], tag, 'COUNTER')
    pushFalcon(endpoint, 'php_listen_queue', phpStatus['listen queue'], tag)
    pushFalcon(endpoint, 'php_max_listen_queue', phpStatus['max listen queue'], tag)
    pushFalcon(endpoint, 'php_slow_per_s', phpStatus['slow requests'], tag, 'COUNTER')
    pushFalcon(endpoint, 'php_active_processes', phpStatus['active processes'], tag)
    pushFalcon(endpoint, 'php_total_processes', phpStatus['total processes'], tag)