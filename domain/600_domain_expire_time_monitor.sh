#!/bin/bash

# 检测域名状态

# 检测whois命令是否存在,不存在则安装jwhois包
function is_install_whois() {
    which whois &> /dev/null
    if [ $? -ne 0 ];then
        yum install -y jwhois
    fi
}

is_install_whois

# 定义需要被检测的域名列表
domain_list=(
baidu.com
)

function check_domain(){
    
domain=$1
ts=$(date +%s)
host_name=`cat /opt/open-falcon-agent/config/open-falcon-agent-cfg.json | grep -v "grep" | grep "hostname" | awk -F ":" '{print $2}' | awk -F '"' '{print $2}'`
#ip_address=`cat /opt/open-falcon-agent/config/open-falcon-agent-cfg.json | grep -v "grep" | grep "hostname" | awk -F ":" '{print $2}' | awk -F '"' '{print $2}' | awk -F "[" '{print $2}' | awk -F ']' '{print $1}'`
step="600"
counterType="GAUGE"

ping -c1 223.5.5.5 &> /dev/null
if [ $? -eq 0 ];then
    domain_tmp=`echo $domain |cut -d '.' -f 2`
    #echo "domain_tmp: ${domain_tmp}"

    # 这里有一个坑,每种主域到期时间的返回的字段不一样,日了狗
    if [ "$domain_tmp" == "com" ];then
        # whois baidu.com | grep "Expiration Date" |awk '{print $5}' | cut -c1-10 | awk -F '-' '{print $1 $2 $3}'
        expire_date=`whois $domain | grep "Expiration Date" |awk '{print $5}' | cut -c1-10 | awk -F '-' '{print $1 $2 $3}'`
        #echo "expire_date.com:${expire_date}"

    elif [ "$domain_tmp" == "cn" ];then
        expire_date=`whois $domain | grep "Expiration Time" | awk '{print $3}' | awk -F '-' '{print $1 $2 $3}'`
        #echo "expire_date.cn:${expire_date}"

    elif [ "$domain_tmp" == "la" ];then
        expire_date=`whois $domain | grep 'Expiry Date' | awk '{print $4}'|cut -d 'T' -f 1`
        #echo "expire_date.la:${expire_date}"
    fi

    # 将日期转化为时间戳
    END_TIME_STAMP=$(date +%s -d "${expire_date}") 
    #echo "domain.expire_date.ts=$END_TIME_STAMP"
    NOW_TIME_STAMP=$(date +%s)
    #echo "now.data.ts=$NOW_TIME_STAMP"

    # 到期时间减去目前时间再转化为天数
    domain_expire_days=$[$[$END_TIME_STAMP-$NOW_TIME_STAMP]/86400]
    #echo "${i}域名离域名到期时间还有${domain_expire_days}天.请注意续费域名..."
    #echo "======================================================"
    metrics="{\"metric\": \"domain.expiredays\", \"endpoint\": \"${host_name}\", \"timestamp\": ${ts},\"step\": ${step},\"value\": ${domain_expire_days},\"counterType\": \"${counterType}\",\"tags\": \"domain_name=${domain}\"}"
    echo "$metrics"
fi
}

for i in ${domain_list[*]}
do
  #echo "dddddd:${i}"
  data=''''${data}','$(check_domain ${i})''''
done

echo "$data"|sed "s/^,//g;s/^/[/g;s/$/]/g"