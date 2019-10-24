#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import requests
import time
import redis

class checkdubbo:
    #green正常，blue没有消费者，red没有提供者
    status_map = {
        'green': 0,
        'blue': 1,
        'red': 2
    }

    def read_endpoint_value(self):
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            load_dict = json.load(f)
            return load_dict["hostname"]

    def con_dubbo(self):
        dubboamdin_ip='127.0.0.1'
        dubboamdin_port='8087'
        list_url='/governance/services'
        url='http://'+dubboamdin_ip+':'+dubboamdin_port+list_url
        payload = ""
        headers = {
            'Authorization': "Basic cm9vdDpoSWx0SVZqM2EwRnJOdTRFMlBMRg==",
            'cache-control': "no-cache"
        }
        response = requests.request("GET", url, data=payload, headers=headers)
        data = response.text
        return data

    def con_redis(self):
        pool = redis.ConnectionPool(host='open-falcon.redis.xxx')
#        pool = redis.ConnectionPool(host='10.200.128.119')
        r = redis.Redis(connection_pool=pool)
    #    r.set('foo','bar')
    #    print (r.get('foo').decode('UTF8'))
        return r

    def falcon(self,hostname,metric_name,tag,ts,value):

        falcon_metrics = {
            'endpoint': hostname,
            'counterType': 'GAUGE',
            'metric': metric_name,
            'tags':  tag,
            'timestamp': ts,
            'step': 60,
            'value': value
        }
        return falcon_metrics

    def dubbolist(self):
        hostname=self.read_endpoint_value()
        #hostname = 'testhost'
        rediscon=self.con_redis()
        ts = int(time.time())
        data = self.con_dubbo()
        g = data.encode("utf-8")
        fo = open('dubbo_cache','w')
        fo.write(g)
        fo.close()
        server_status = []
        dubbo_status = []
        falcon_metrics = []
        with open('dubbo_cache','r') as file:
            for line in file.readlines():
                if 'checkbox' in line and 'value' in line:
                    server_name = line.split("\"")[5].split("\"")[0]
                #    server_name_line = server_name.replace(".","-",10)
                    server_status.append(server_name)
                elif 'font color' in line:
                    status = line.split("\"")[1].split("\"")[0]
                    dubbo_status.append(status)
        len_name =len(server_status)
        len_status = len(dubbo_status)
        if len_name == len_status:
            for num in range(0,len_name):
                value = self.status_map[dubbo_status[num]]
                metric_name = "dubbo.status"
                tag = 'sname='+server_status[num]
                falcon_metric=self.falcon(hostname,metric_name,tag,ts,value)
                falcon_metrics.append(falcon_metric)
                old_value = rediscon.get(server_status[num])
                #检查dubbo服务，和上一次状态对比，1为没消费者，2为没有提供者，0恢复告警
                metric_name = 'dubbo.check'
                if old_value == None:
	            pass
         #           print(server_status[num]+"为新增服务")
                else:
                    if int(old_value) == 0:
                        if int(value) == 0:
                            check_value = 0
                        elif int(value) == 1:
                            check_value = 1
                        elif int(value) == 2:
                            check_value = 2
                        falcon_metric = self.falcon(hostname, metric_name, tag, ts, check_value)
                        falcon_metrics.append(falcon_metric)
                rediscon.set(server_status[num],value)
            print json.dumps(falcon_metrics)
        else:
            print("服务名与状态值数量不相等，数据混乱")




if __name__ == '__main__':
    try:
        check=checkdubbo()
        check.dubbolist()
    except Exception as e:
        print e