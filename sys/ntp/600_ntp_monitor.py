#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import json
import os
import time


def read_endpoint_value():
    try:
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            load_dict = json.load(f)
            return load_dict["hostname"]

    except OSError:
        pass

def fetch_ntp_state():

    # fail    获取状态: 0 获取成功, 1 获取失败
    # offset  ntp同步的偏移量, 使用绝对值表示
    # timeout 超时状态: 0 成功,     1 超时
    offset, fail, timeout = 0, 1, 0

    hostname = read_endpoint_value()

    try:
        raw_data = Popen(['ntpq', '-pn'], stdout=PIPE, stderr=PIPE).communicate()[0]
        for line in raw_data.splitlines():
            if line.startswith('*'):
                l = line.split()
                when, poll, offset = l[4], l[5], l[8]
                offset = abs(float(offset))
                timeout, fail = check_status(when, poll)

    except OSError:
        pass

    create_record(hostname, 'sys.ntp.fail', fail)
    create_record(hostname, 'sys.ntp.timeout', timeout)
    create_record(hostname, 'sys.ntp.offset', offset)


# 判断上次同步状态, return (timeout, fail)
def check_status(when, poll):

    timeout, fail = 0, 1
    try:
        if int(poll) - int(when) >= 0:
            timeout, fail = 0, 0
        else:
            timeout, fail = 1, 0
    except:
        pass

    return timeout, fail

def create_record(hostname, metric, value):
    record = {}
    record['Metric']      = metric
    record['Endpoint']    = hostname
    record['Timestamp']   = int(time.time())
    record['Step']        = 600
    record['Value']       = value
    record['CounterType'] = 'GAUGE'
    record['TAGS']        = ''
    data.append(record)

if __name__ == '__main__':

    retry = 3
    retry_interval = 3

    for i in range(0, retry):

        data = []
        fetch_ntp_state()

        if data[0]['Value'] == 0 and data[1]['Value'] == 0 or retry == i+1:
            break
        time.sleep(retry_interval)
    
    print json.dumps(data)