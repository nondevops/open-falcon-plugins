#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os,sys
import os.path
from os.path import isfile
from traceback import format_exc
import xmlrpclib
import socket
import time
import json
import copy
import httplib



timestamp = int(time.time())
step = 60

def read_endpoint_value():
    try:
        with open('/opt/open-falcon-agent/config/open-falcon-agent-cfg.json', 'r') as f:
            load_dict = json.load(f)
            return load_dict["hostname"]

    except OSError:
        pass

class Resource():

    def __init__(self, pid, tag):
        self.host = read_endpoint_value()
        self.pid = pid
        self.tag = tag

    def get_cpu_user(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $14+$16}'"
        return os.popen(cmd).read().strip("\n")

    def get_cpu_sys(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $15+$17}'"
        return os.popen(cmd).read().strip("\n")

    def get_cpu_all(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $14+$15+$16+$17}'"
        return os.popen(cmd).read().strip("\n")

    # 进程总内存(文件映射，共享内存，堆，任何其它的内存的总和，它包含VmRSS)
    def get_mem_vmsize(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep VmSize | awk '{print $2*1024}'"
        return os.popen(cmd).read().strip("\n")
    
    # 进程实际用到的物理内存
    def get_mem_vmrss(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep VmRSS | awk '{print $2*1024}'"
        return os.popen(cmd).read().strip("\n")

    def get_mem_swap(self):
        cmd = "cat /proc/" + str(self.pid) + "/stat | awk '{print $(NF-7)+$(NF-8)}' "
        return os.popen(cmd).read().strip("\n")

    def get_fd(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep FDSize | awk '{print $2}'"
        return os.popen(cmd).read().strip("\n")

    def get_process_status(self):
        cmd = "cat /proc/" + str(self.pid) + "/status | grep State | awk '{print $2}'"
        return os.popen(cmd).read().strip("\n")

    def run(self):
        self.resources_d = {
            'process.cpu.user':[self.get_cpu_user,'COUNTER'],
            'process.cpu.sys':[self.get_cpu_sys,'COUNTER'],
            'process.cpu.all':[self.get_cpu_all,'COUNTER'],
            'process.mem.vmsize':[self.get_mem_vmsize,'GAUGE'],
            'process.mem.used':[self.get_mem_vmrss,'GAUGE'],
            'process.mem.swap':[self.get_mem_swap,'GAUGE'],
            'process.fdsize':[self.get_fd,'GAUGE'],
            'process.status':[self.get_process_status,'GAUGE']
        }

        if not os.path.isdir("/proc/" + str(self.pid)):
            return

        output = []
        for resource in self.resources_d.keys():
                t = {}
                t['endpoint'] = self.host
                t['timestamp'] = timestamp
                t['step'] = step
                t['counterType'] = self.resources_d[resource][1]
                t['metric'] = resource
                t['value'] = self.resources_d[resource][0]()
                #t['tags'] = "module=cpu_resource,pro_cmd=%s" % ( self.tag)
                t['tags'] = "process_cmd=%s,process_pid=%s" % (self.tag, self.pid)

                output.append(t)

        return output

def get_pid():
    # cpu使用大于80或内存大于80, 取排名前3的进程
    cmd = "ps aux | awk '{ if ($3>80 || $4>80) print $2, $3, $4, $11$12; }' | sort -k2rn | head -n 3"
    ret = []
    for item in os.popen(cmd).readlines():
        pid = {}
        try:
            assert(isinstance(int(item.split()[0]), (int, long)))
        except AssertionError:
            #print "ERROR: key is not int."
            continue
        pid[int(item.split()[0])] = item.split()[-1].strip("\n")
        ret.append(pid)
    return ret

if __name__ == "__main__":
    pids = get_pid()
    #print pids
    payload = []
    for item in pids:
        for pid in item:            
            d = Resource(pid=pid, tag=item[pid]).run()
            if d:
                payload.extend(d)
    if payload:
        print json.dumps(payload)
