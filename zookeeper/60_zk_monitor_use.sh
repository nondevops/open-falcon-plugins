#!/bin/bash
# 系统环境
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin

# 全局变量
endpoint="cq-dubbo-zookeeper.0903261015.perf.bj[10.200.75.19]"
timenow=`date +%s`
valuetype="GAUGE"
step="60"

# 获取zookeeper数据，端口号根据实际情况修改
echo stat | nc 127.0.0.1 2181 > /tmp/tmp.stat
echo wchs | nc 127.0.0.1 2181 > /tmp/tmp.wchs
echo ruok | nc 127.0.0.1 2181 > /tmp/tmp.ruok

# stat 命令的结果处理
zookeeper_stat_received=`cat /tmp/tmp.stat | grep "Received:" | awk '{print $2}'`
zookeeper_stat_sent=`cat /tmp/tmp.stat | grep "Sent:" | awk '{print $2}'`
zookeeper_stat_clients=`cat /tmp/tmp.stat | grep "sent" | wc -l`
zookeeper_stat_outstanding=`cat /tmp/tmp.stat | grep "Outstanding:" | awk '{print $2}'`
zookeeper_stat_nodecount=`cat /tmp/tmp.stat | grep "Node count:" | awk '{print $3}'`

# wchs 命令的结果处理
zookeeper_wchs_connections=`cat /tmp/tmp.wchs | head -n1 | awk '{print $1}'`
zookeeper_wchs_watchingpaths=`cat /tmp/tmp.wchs | head -n1 | awk '{print $4}'`
zookeeper_wchs_totalwatches=`cat /tmp/tmp.wchs | grep 'Total watches' | awk -F\: '{print $2}'`

# ruok 命令的结果处理
zookeeper_ruok=`cat /tmp/tmp.ruok | grep 'imok' | wc -l`

# 删除临时文件
rm -f /tmp/tmp.stat /tmp/tmp.wchs /tmp/tmp.ruok

# 声明一个关联数组，将metric与value组成key-value对
declare -A zk_arr
zk_arr=(["zookeeper_stat_received"]="$zookeeper_stat_received" ["zookeeper_stat_sent"]="$zookeeper_stat_sent" ["zookeeper_stat_clients"]="$zookeeper_stat_clients" ["zookeeper_stat_outstanding"]="$zookeeper_stat_outstanding" ["zookeeper_stat_nodecount"]="$zookeeper_stat_nodecount" ["zookeeper_wchs_connections"]="$zookeeper_wchs_connections" ["zookeeper_wchs_watchingpaths"]="$zookeeper_wchs_watchingpaths" ["zookeeper_wchs_totalwatches"]="$zookeeper_wchs_totalwatches" ["zookeeper_ruok"]="$zookeeper_ruok")

for key in ${!zk_arr[@]}
do
	echo "$key ==> ${zk_arr[$key]}"
	# curl -X POST -d "[{
    # 		\"metric\": \"$key\",
    # 		\"endpoint\": \"$endpoint\",
    # 		\"timestamp\": $timenow,
    # 		\"step\": \"$step\",
    # 		\"value\": \"${zk_arr[$key]}\",
    # 		\"counterType\": \"$valuetype\",
    # 		\"tags\": \"name=dubbo_zookeeper\"
	# 	}]" http://127.0.0.1:11988/v1/push
done
