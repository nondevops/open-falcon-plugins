#-*- coding:utf-8 -*-

import os, sys, re
import json
import requests
import time
import urllib2, base64
from socket import *

timestamp = int(time.time())
step = 60
counterType = "GAUGE"
data = []


def checkPing(host):
    result=os.popen("ping -i 0.1 -c 10 %s | tail -n 2 | tail -n 1 | awk -F\/ '{print $5}'" % host).read()
    try:
        result=int(float(result.replace("\n",'')))
    except:
        result = -1
    return result

def read_endpoint_value(self):
    try:
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            load_dict = json.load(f)
            return load_dict["hostname"]
    except OSError:
        pass

# 准备上报数据
def zuzhuangData(tags = '', value = ''):
    endpoint = "172.16.10.99"
    metric = "other_ip.loss.percent"
    key = "icmp"
    timestamp = int(time.time())
    step = 60
    vtype = "GAUGE"

    i = {
            'Metric' :'%s.%s'%(metric,key),
            'Endpoint': endpoint,
            'Timestamp': timestamp,
            'Step': step,
            'value': value,
            'CounterType': vtype,
            'TAGS': tags
            }
    return i

p = []
with open("./icmp.txt") as f:
    for line in f:
        results = re.findall("(\S+)",line)
        #print results
        host = results[0]
        description = results[1]
        tags = "project=ops,"
        tags += "host=%s,description=%s"%(host,description)
        value = checkPing(host)
        p.append(zuzhuangData(tags,value))

print(json.dumps(p, sort_keys=True,indent = 4))