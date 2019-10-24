
#!/usr/bin/env python
import re
import sys
import time
import socket
import json
import requests
import subprocess
def execute(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return p.communicate()
def Get_manufacturer():
    cmd= """/usr/sbin/dmidecode | grep -A1 'System Information' | grep 'Manufacturer'"""
    stdout, stderr = execute(cmd)
    return stdout.split(':')[1].strip()
# 1-OK , 0-ERROR
def CheckMem(ip,timestamp,step,manufacturer=Get_manufacturer()):
    if  manufacturer == 'Dell Inc.':
        cmd = "/opt/dell/srvadmin/sbin/omreport chassis memory | grep 'Health' | awk -F ':' '{ print $2 }'" 
    elif manufacturer == 'HP':
    	cmd = "hpasmcli -s 'show dimm' | grep Status | awk  '{print $2}'"
    else:
        cmd = ""
    stdout, stderr = execute(cmd)
    status = '1'
    p = []
    for i in stdout.splitlines():
	if 'OK' == i.strip().upper():
	    pass
	else:
	    status = '0'
    item = {
        "Metric": "hw1.mem.status",
	"Endpoint": ip,
	"Timestamp": timestamp,
	"Step": step,
	"Value": int(status),
	"CounterType": "GAUGE"
    }
    item = json.dumps(item)
    p.append(item)
    return p   
def CheckPower(ip,timestamp,step,manufacturer=Get_manufacturer()):
    if  manufacturer == 'Dell Inc.':
        cmd = "/opt/dell/srvadmin/sbin/omreport chassis pwrsupplies | grep ^Status | awk '{print $3}'"
    elif manufacturer == 'HP':
        cmd = "hpasmcli -s 'show POWERSUPPLY' |grep Condition | awk '{print $2}'"
    else:
        cmd = ""
    stdout, stderr = execute(cmd)
    status = '1'
    p = []
    for i in stdout.splitlines():
        if 'OK' == i.strip().upper():
            pass
        else:
            status = '0'
            break
    item = {
        "Metric": "hw1.power.status",
        "Endpoint": ip,
        "Timestamp": timestamp,
        "Step": step,
        "Value": int(status),
        "CounterType": "GAUGE"
    }
    item = json.dumps(item)
    p.append(item)
    return p
def CheckCPU(ip,timestamp,step,manufacturer=Get_manufacturer()):
    if  manufacturer == 'Dell Inc.':
        cmd = "/opt/dell/srvadmin/sbin/omreport chassis processors | grep ^Status|awk '{print $3}'"
    elif manufacturer == 'HP':
        cmd = "hpasmcli -s 'show SERVER' | grep Status |awk '{print $3}'"
    else:
        cmd = ""
    stdout, stderr = execute(cmd)
    status = '1'
    p = []
    for i in stdout.splitlines():
        if 'OK' == i.strip().upper():
            pass
        else:
            status = '0'
            break
    item = {
        "Metric": "hw1.cpu.status",
        "Endpoint": ip,
        "Timestamp": timestamp,
        "Step": step,
        "Value": int(status),
        "CounterType": "GAUGE"
    }
    item = json.dumps(item)
    p.append(item)
    return p
def CheckCPUTemp(ip,timestamp,step,manufacturer=Get_manufacturer()):
    if  manufacturer == 'Dell Inc.':
        cpu_temp = "/opt/dell/srvadmin/sbin/omreport  chassis temps | grep -A 1 CPU | grep Reading | awk -F ':' '{ print $2 }' | awk '{ print $1 }'"
    elif manufacturer == 'HP':
        cpu_temp = "hpasmcli -s 'SHOW TEMP' | grep CPU | awk '{print $3}' | cut -b 1-2"
    else:
        cpu_temp = ''
    stdout, stderr = execute(cpu_temp)
    p = []
    x = 1
    for i in stdout.splitlines():
        item = {
            "Metric": "hw1.cpu%s.temp" % x,
            "Endpoint": ip,
            "Timestamp": timestamp,
            "Step": step,
            "Value": i.split('.')[0],
            "CounterType": "GAUGE"
        }
 
        x = x+1      
	item = json.dumps(item)
        p.append(item)
    return p
def CheckDiskCtl(ip,timestamp,step,manufacturer=Get_manufacturer()):
    if  manufacturer == 'Dell Inc.':
        cmd = "/opt/dell/srvadmin/sbin/omreport storage controller | grep ^ID | awk -F':' '{ print $2  }'"
        stdout, stderr = execute(cmd)
        controller = stdout.splitlines()
        ctl_status = "/opt/dell/srvadmin/sbin/omreport storage adisk controller=%s | grep ^Status | awk -F':' '{ print $2 }'" %controller[0].strip()
    elif  manufacturer == 'HP':
        cmd = "/opt/hp/hpssacli/bld/hpssacli ctrl all show detail | grep 'Slot:' |awk -F':' '{ print $2 }'"
        stdout, stderr = execute(cmd)
        controller = stdout.splitlines()
        ctl_status = "/opt/hp/hpssacli/bld/hpssacli ctrl slot=%s pd all show status | grep 'Controller Status'|awk '{print $3}'" %controller[0].strip().strip()
    else:
        ctl_status = ""
    p = []
    status = '1'
    stdout, stderr = execute(ctl_status)
    for i in stdout.splitlines():
	if 'OK' == i.strip().upper():
            pass
        else:
            status = '0'
            break
    item = {
        "Metric": "hw1.ctl.status",
        "Endpoint": ip,
        "Timestamp": timestamp,
        "Step": step,
        "Value": int(status),
        "CounterType": "GAUGE"
    }
    item = json.dumps(item)
    p.append(item)
    return p
def main():
    ip = socket.gethostname()
    timestamp = int(time.time())
    step = 60
    x = []
    for i in CheckMem(ip,timestamp,step):
	x.append(i)
    for i in CheckPower(ip,timestamp,step):
	x.append(i)
    for i in CheckCPU(ip,timestamp,step):
	x.append(i)
    for i in CheckCPUTemp(ip,timestamp,step):
	x.append(i)
    for i in CheckDiskCtl(ip,timestamp,step):
	x.append(i)
    print '[%s]' % ','.join(x)
if __name__ == '__main__':
    cmd = "dmidecode | grep 'Product Name'"
    stdout, stderr = execute(cmd)
    if stdout.split(':')[1].strip() == 'KVM':
        sys.exit()
    main()