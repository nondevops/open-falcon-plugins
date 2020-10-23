#!/usr/bin/python
#--encoding:utf8

import os
import sys
import re
import pprint
import time
import json
import requests
import time
import ast
import yaml

# 定义falcon上报数据的时候用到的变量
falconTs = int(time.time())
falconEndpoint = "cluster-fastdfs"
falconTimeStamp = 60
falconPayload=[]
falconAgentUrl="http://127.0.0.1:11988/v1/push"

# 对于monitor监控到的数据，用以下的变量去存放采集到的数据
serverinfo={}
currentGroupNumber=""
currentStorageNumber=""

# 执行命令
cmdLine = "/home/machtalk/opt/fastdfs/usr/bin/fdfs_monitor /home/machtalk/opt/fastdfs/etc/fdfs/client.conf"
cmdResult = os.popen(cmdLine).readlines()

# 定义函数，由于采集到的数据有好几种格式
# 100， 数值
# 5.05， 版本号
# 2016-10-10 10:10:10， 时间格式
# 10.10.10.10， ip地址格式
# ACTIVE， 存货代表1，其他使用0
# 该函数会把这些转换为float类型或者整形。
def falconValue(value):
    result = re.findall("(\d+\-\d+\-\d+ \d+\:\d+\:\d+)",value)
    if len(result) != 0:
        timeString = result[0]
        timeTP = time.strptime(timeString,"%Y-%m-%d %H:%M:%S")
        timeStamp = time.mktime(timeTP)
        return int(timeStamp)
    result = re.findall("(\d+\.\d+\.\d+\.\d+$)",value)
    if len(result) == 1:
        result=result[0].split(".")
        #print result
        #print int(float(result[0])) * (2**24) + int(float(result[1])) * (2**16) + int(float(result[2])) * (2**8) + int(float(result[3]))
        return int(float(result[0])) * (2**24) + int(float(result[1])) * (2**16) + int(float(result[2])) * (2**8) + int(float(result[3]))
    result = re.findall("(\d+) MB$",value)
    if len(result) == 1:    
        return float(result[0]) * 1024 * 1024
    result = re.findall("(ACTIVE)",value)
    if len(result) == 1:
        return 1
    result = re.findall("(IP_CHANGED)",value)
    if len(result) == 1:
        return -1
    result = re.findall("(\d+\.\d+$)",value)
    if len(result) == 1:
        return value
    result = re.findall("(\d+$)",value)
    if len(result) == 1:
        return value
    else:
        print "异常"
        return -1

# 默认采用GAUGE的形式，如果有COUNTER类型，尤其是时间类型，那么就加入下面的列表
def falconType(value):
    counterTypeList = []
    counterTypeList.append("up time")
    counterTypeList.append("join time")
    counterTypeList.append("last_heart_beat_time")
    counterTypeList.extend(["success_append_count","success_create_link_count","success_delete_count","success_delete_link_count","success_download_count","success_file_open_count","success_file_read_count","success_file_write_count","success_get_meta_count","success_modify_count","success_set_meta_count","success_truncate_count","success_upload_count"])
    if value in counterTypeList:
        return "COUNTER"
    return "GAUGE"

# 根据之前的cmdline执行结果，进行处理
for line in cmdResult:
    # check server_count 和 server_index
    result1=re.findall("server_count=(\d+), server_index=(\w+)",line)
    if len(result1)==1:
    	serverinfo['server_count'] = result1[0][0]
    	serverinfo['server_index'] = result1[0][1]
        payloadString="""{ "endpoint": "%s", "metric": "%s", "timestamp": %s, "step": %s, "value": %s, "counterType": "%s", "tags": "%s"} """%(falconEndpoint, "fdfs.server_count", falconTs, falconTimeStamp, falconValue(serverinfo['server_count']),"GAUGE","")
        falconPayload.append(yaml.load(payloadString))
        payloadString="""{ "endpoint": "%s", "metric": "%s", "timestamp": %s, "step": %s, "value": %s, "counterType": "%s", "tags": "%s"} """%(falconEndpoint, "fdfs.server_index", falconTs, falconTimeStamp, falconValue(serverinfo['server_index']),"GAUGE","")
        falconPayload.append(yaml.load(payloadString))
        continue
    # check group count
    result2=re.findall("group count: (\d+)",line) 
    if len(result2) == 1:
	serverinfo['group_count'] = result2[0]
        payloadString="""{ "endpoint": "%s", "metric": "%s", "timestamp": %s, "step": %s, "value": %s, "counterType": "%s", "tags": "%s"} """%(falconEndpoint, "fdfs.group_count", falconTs, falconTimeStamp, falconValue(serverinfo['group_count']),"GAUGE","")
        falconPayload.append(yaml.load(payloadString))
        #print serverinfo
        continue
    # 如果遇到Group 1
    result3=re.findall("Group (\d+)",line)
    if len(result3) == 1:
        currentGroupNumber="%s"%result3[0]
        serverinfo[currentGroupNumber] = {}
        #print "找到currentGroupNumber%s"%(currentGroupNumber)
        continue
    # 开始解析Group下面的
    groupInfoList = ["group name", "disk total space", "disk free space", "trunk free space", "storage server count", "active server count", "storage server port", "storage HTTP port", "store path count", "subdir count per path", "current write server index", "current trunk file id"]
    for groupInfo in groupInfoList:
        result = re.findall("%s = (.+)"%(groupInfo),line)
        if len(result) ==1:
            serverinfo[currentGroupNumber][groupInfo] = result[0]
            payloadString="""{ "endpoint": "%s", "metric": "%s", "timestamp": %s, "step": %s, "value": %s, "counterType": "%s", "tags": "%s"} """%(falconEndpoint, "fdfs."+groupInfo, falconTs, falconTimeStamp, falconValue(serverinfo[currentGroupNumber][groupInfo]),falconType(groupInfo),"group="+currentGroupNumber)
            falconPayload.append(yaml.load(payloadString))
            break
    # Storage 1:
    result16 = re.findall("Storage (\d+):",line)
    if len(result16) == 1:
        print result16
        currentStorageNumber = result16[0]
        serverinfo[currentGroupNumber][currentStorageNumber]={}
        #print "遇到了新的Storage:%s"%(currentStorageNumber)
        continue
    # 使用列表去处理
    storage_item_list=["id","ip_addr","http domain","version","join time","up time","total storage","free storage","upload priority","store_path_count","subdir_count_per_path","storage_port","storage_http_port","current_write_path","source","if_trunk_server","connection.alloc_count","connection.current_count","connection.max_count","total_upload_count","success_upload_count","total_append_count","success_append_count","total_modify_count","success_modify_count","total_truncate_count","success_truncate_count","total_set_meta_count","success_set_meta_count","total_delete_count","success_delete_count","total_download_count","success_download_count","total_get_meta_count","success_get_meta_count","total_create_link_count","success_create_link_count","total_delete_link_count","success_delete_link_count","total_upload_bytes","success_upload_bytes","total_append_bytes","success_append_bytes","total_modify_bytes","success_modify_bytes","stotal_download_bytes","success_download_bytes","total_sync_in_bytes","success_sync_in_bytes","total_sync_out_bytes","success_sync_out_bytes","total_file_open_count","success_file_open_count","total_file_read_count","success_file_read_count","total_file_write_count","success_file_write_count","last_heart_beat_time","last_source_update","last_sync_update","last_synced_timestamp", "connection.alloc_count","connection.current_count","connection.max_count","total_upload_count","success_upload_count","total_append_count","success_append_count","total_modify_count","success_modify_count","total_truncate_count","success_truncate_count","total_set_meta_count","success_set_meta_count","total_delete_count","success_delete_count","total_download_count","success_download_count","total_get_meta_count","success_get_meta_count","total_create_link_count","success_create_link_count","total_delete_link_count","success_delete_link_count","total_upload_bytes","success_upload_bytes","total_append_bytes","success_append_bytes","total_modify_bytes","success_modify_bytes","stotal_download_bytes","success_download_bytes","total_sync_in_bytes","success_sync_in_bytes","total_sync_out_bytes","success_sync_out_bytes","total_file_open_count","success_file_open_count","total_file_read_count","success_file_read_count","total_file_write_count","success_file_write_count","last_heart_beat_time","last_source_update","last_sync_update","last_synced_timestamp"]
    for storage_item in storage_item_list:
        print "开始寻找"+storage_item
        result = re.findall("^\s+%s = ([\S ]+)"%storage_item,line)
        if len(result) == 1:
	    #print "发现匹配",
            #print line
            #print result
            serverinfo[currentGroupNumber][currentStorageNumber][storage_item] = result[0]
            payloadString="""{ "endpoint": "%s", "metric": "%s", "timestamp": %s, "step": %s, "value": %s, "counterType": "%s", "tags": "%s"} """%(falconEndpoint, "fdfs."+storage_item, falconTs, falconTimeStamp, falconValue(serverinfo[currentGroupNumber][currentStorageNumber][storage_item]),falconType(storage_item),"group="+currentGroupNumber+",storage="+currentStorageNumber)
            falconPayload.append(yaml.load(payloadString))
            break

# 以下主要用于打印测试，pprint这个不错，可以格式化列表或者字典
#print serverinfo
#print len(serverinfo)
#pp = pprint.PrettyPrinter(indent = 4)
#pp.pprint(serverinfo)
#pp.pprint(falconPayload)
#print type(falconPayload)
#print len(falconPayload)
#print type(falconPayload[0])
#print json.dumps(falconPayload)

r = requests.post(falconAgentUrl, data=json.dumps(falconPayload))
print r.text