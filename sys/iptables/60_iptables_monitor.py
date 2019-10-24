#!/usr/bin/env python  
# -*- coding:utf-8 -*- 
# __time__   = '2018/5/28 10:31'

import os
import json
import time


class IptablesStatus(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.metric = "monitor.iptables_status"
        self.counter_type = "GAUGE"
        self.step = 60
        self.tags = u"防火墙运行状态"
        self.commandline = "service iptables status"

    def get_endpoint(self):
        if not os.path.exists(self.config_file):
            return ""
        with open(self.config_file, 'r') as fp:
            config_dict = json.load(fp)
            endpoint = config_dict.get("hostname")
            return endpoint.encode("utf8")

    def get_value(self):
        stdout = os.popen(self.commandline)
        line_one = stdout.readline().strip()
        if line_one in ["iptables：未运行防火墙。", "iptables: Firewall is not running."]:
            return 0
        return 1
    
    def output(self):
        data = [{
            "endpoint": self.get_endpoint(),
            "tags": self.tags,
            "timestamp": int(time.time()),
            "metric": self.metric,
            "value": self.get_value(),
            "counterType": self.counter_type,
            "step": self.step

        }]
        return json.dumps(data)


if __name__ == '__main__':
    agent_config = "/data/app/open-falcon/agent/cfg.json"
    obj = IptablesStatus(agent_config)
    print obj.output()