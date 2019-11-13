#!/bin/bash

# 检测证书状态

domain_list=(
baidu.com
)

function check_ssl(){
domain=$1
ts=$(date +%s)
host_name=`cat /opt/open-falcon-agent/config/open-falcon-agent-cfg.json | grep -v "grep" | grep "hostname" | awk -F ":" '{print $2}' | awk -F '"' '{print $2}'`
#ip_address=`cat /opt/open-falcon-agent/config/open-falcon-agent-cfg.json | grep -v "grep" | grep "hostname" | awk -F ":" '{print $2}' | awk -F '"' '{print $2}' | awk -F "[" '{print $2}' | awk -F ']' '{print $1}'`
step="600"
counterType="GAUGE"

ping -c1 223.5.5.5 &> /dev/null
if [ $? -eq 0 ]
then
    END_TIME=$(echo | timeout 3 openssl s_client -servername ${domain} -connect "${domain}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | awk -F '=' '{print $2}' )
    #将日期转化为时间戳
    END_TIME_STAMP=$(date +%s -d "${END_TIME}") 
    #echo "cccccc=$END_TIME1"
    NOW_TIME__STAMP=$(date +%s)
    #echo "ddddddd=$NOW_TIME"
    # 到期时间减去目前时间再转化为天数
    ssl_expire_days=$(($((${END_TIME_STAMP} - ${NOW_TIME__STAMP}))/(60*60*24))) 
    #echo "域名${domain}的证书还有${ssl_expire_days}天过期..."
    metrics="{\"metric\": \"ssl.cert.expiredays\", \"endpoint\": \"${host_name}\", \"timestamp\": ${ts},\"step\": ${step},\"value\": ${ssl_expire_days},\"counterType\": \"${counterType}\",\"tags\": \"domain_name=${domain}\"}"
    echo $metrics
else
    pass
fi
}

for i in ${domain_list[*]}
do
  data=''''${data}','$(check_ssl ${i})''''
done

echo "$data"|sed "s/^,//g;s/^/[/g;s/$/]/g"
