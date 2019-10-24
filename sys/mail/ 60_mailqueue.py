#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time

data = []
queue_name = ('active', 'deferred', 'maildrop', 'incoming', 'corrupt', 'hold')
spool_dir = '/var/spool/postfix/'

def read_endpoint_value():
    try:
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            load_dict = json.load(f)
            return load_dict["hostname"]

    except OSError:
        pass

def fetch_queue_length(queue):
    length = 0
    path = spool_dir + queue
    for root, _, files in os.walk(path):
        length += len(files)
    return length

def create_record(hostname, queue, value):
    record = {}
    record['metric'] = 'sys.mail.queue.%s' % queue
    record['endpoint'] = hostname
    record['timestamp'] = int(time.time())
    record['step'] = 60
    record['value'] = int(value)
    record['counterType'] = 'GAUGE'
    record['tags'] = ''
    data.append(record)

for queue in queue_name:
    hostname = read_endpoint_value()
    create_record(hostname, queue, fetch_queue_length(queue))

if data:
    print json.dumps(data)