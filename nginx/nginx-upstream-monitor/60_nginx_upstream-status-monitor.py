#!/usr/bin/env python
import requests
import time
import json
import re
import os

endpoint = "default"
ip = '127.0.0.1'
ts = int(time.time())
step = 60
counter_list = []


def get_nginx_status():
    url = 'http://%s/Nginx_Upstream_Status' % ip
    try:
        response = requests.get(url, timeout=1)
    except:
        return False
    if response.status_code == 200:
        for line in response.text.split('\n'):
            if re.search('Active connections', line):
                value = int(line.split(':')[1])
                counter_list.append(
                    {"endpoint": endpoint,
                     "metric": "nginx.active_connections",
                     "tags": "",
                     "timestamp": ts,
                     "step": step,
                     "counterType": "GAUGE",
                     "value": value})
            if re.search('Reading', line):
                counter_list.append(
                    {"endpoint": endpoint,
                     "metric": "nginx.reading",
                     "tags": "",
                     "timestamp": ts,
                     "step": step,
                     "counterType": "GAUGE",
                     "value": int(line.split()[1])})
                counter_list.append(
                    {"endpoint": endpoint,
                     "metric": "nginx.writing",
                     "tags": "",
                     "timestamp": ts,
                     "step": step,
                     "counterType": "GAUGE",
                     "value": int(line.split()[3])})
                counter_list.append(
                    {"endpoint": endpoint,
                     "metric": "nginx.waiting",
                     "tags": "",
                     "timestamp": ts,
                     "step": step,
                     "counterType": "GAUGE",
                     "value": int(line.split()[5])})
    return True


def get_down_upstream():
    url = 'http://%s/_Check_Status?format=json' % ip
    try:
        response = requests.get(url, timeout=1)

    except:
        return False
    if response.status_code == 200:
        c = response.json()
        for i in c['servers']['server']:
            if i['status'] == 'down':
                if "_bjzw_" in i['upstream'] or "_tjhy_" in i['upstream']:
                    continue
                p = {"endpoint": endpoint,
                     "metric": "nginx.upstream",
                     "tags": "upstream=%s,ip=%s" % (i['upstream'], i['name']),
                     "timestamp": ts,
                     "step": step,
                     "counterType": "GAUGE",
                     "value": 0}
                counter_list.append(p)
    return True


if __name__ == '__main__':
    try:
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            json_file = json.loads(f.read())
            endpoint = json_file['hostname']
    except:
        os._exit(1)
    n = get_nginx_status()
    u = False
    if "docker-" not in endpoint:
       u = get_down_upstream()
    if n or u:
        print json.dumps(counter_list)
