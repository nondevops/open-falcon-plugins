#!/bin/bash

# 对CMDB存在的内网实例ping检测,监控丢包率

TS=$(date +%s)
HOSTNAME=`cat /opt/open-falcon-agent/config/open-falcon-agent-cfg.json | grep -v "grep" | grep "hostname" | awk -F ":" '{print $2}' | awk -F '"' '{print $2}'`
ip_address=`cat /opt/open-falcon-agent/config/open-falcon-agent-cfg.json | grep -v "grep" | grep "hostname" | awk -F ":" '{print $2}' | awk -F '"' '{print $2}' | awk -F "[" '{print $2}' | awk -F ']' '{print $1}'`
step="60"
counterType="GAUGE"
pings="/bin/ping"

# -c 次数; -w ping退出之前的超时秒数; -W 等待超时时间s; -q 静默输出
# ping -c 50 -w 10 -W 10 -q "10.200.7.106" | grep -oE "[0-9]*% packet loss" | awk -F'%' '{print $1}'
loss=$($pings -c 50 -w 10 -W 10 -q "${ip_address}" | grep -oE "[0-9]*% packet loss" | awk -F'%' '{print $1}')

metrics="[{\"metric\": \"cmdb_inner_instance_ip.loss.percent\", \"endpoint\": \"$HOSTNAME\", \"timestamp\": $TS,\"step\": $step,\"value\": $loss,\"counterType\": \"${counterType}\",\"tags\": \"ip=${ip_address}\"}]"
echo $metrics


#echo "${ip} loss percentage: ${loss}%"
#curl -X POST -d "[{\"metric\": \"ip.loss.percent\", \"endpoint\": \"$HOSTNAME\", \"timestamp\": $TS,\"step\": $step,\"value\": $loss,\"counterType\": \"GAUGE\",\"tags\": \"ip=${ip_address}\"}]" http://127.0.0.1:11988/v1/push