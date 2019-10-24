#!/usr/bin/env python
import time
import json
import os
import commands

endpoint = "default"
ts = int(time.time())
step = 1800
counter_list = []


def checknginxconf():
    b = False
    val = commands.getoutput('nginx -t')
    if 'syntax is ok' in val:
        b = True
    return b


if __name__ == '__main__':
    try:
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            json_file = json.loads(f.read())
            endpoint = json_file['hostname']
    except:
        os._exit(1)
    value = 0
    if checknginxconf():
        value = 1
    counter_list.append(
        {"endpoint": endpoint,
         "metric": "nginx.conf",
         "tags": "",
         "timestamp": ts,
         "step": step,
         "counterType": "GAUGE",
         "value": value})
    print json.dumps(counter_list)