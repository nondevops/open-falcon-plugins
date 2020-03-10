#!/bin/bash

## 警告级别_执行_重启_java_tomcat
## waring_exec_restart_java_tomcat

reboot_tomcat(){
# grep "JAVA_WAR=" /etc/javaguard.conf |awk -F= '{print $2}' |awk -F"." '{print $1}'| tr -d " | tr -d '
project=`grep "JAVA_WAR=" /etc/javaguard.conf |awk -F= '{print $2}' |awk -F"." '{print $1}' | tr -d '"' | tr -d " "`
before_status=`curl -I -s --connect-timeout 10 -m 20 127.0.0.1:8088/$project/check | grep HTTP | awk '{print $2}'`
echo "项目名：$project"
echo "重启前check状态：$before_status"
/etc/init.d/java-guard offline
/etc/init.d/tomcat restart

sleep 60

if [ "$before_status" == 200 ];then
  for ((a=0;a<10;a++))
  do
    status=""
    last_status=`curl -I -s --connect-timeout 10 -m 20 127.0.0.1:8088/$project/check | grep HTTP | awk '{print $2}'`
    curl -I -s --connect-timeout 10 -m 20 127.0.0.1:8088/$project/check|grep HTTP|grep 200 > /dev/null
    if [ $? == 0 ];then
      /etc/init.d/java-guard online
      echo "重启后check状态：$last_status"
      echo "$project 重启成功，重启后check状态：$last_status"
      break
    else
      status=`echo "$project 重启失败,重启前zbjche状态为$before_status,重启后状态为$last_status"`
    fi
    sleep 5
  done
else
  /etc/init.d/java-guard online
  echo -e "033[31m 由于$project 未接入check，故无法判定是否成功启动，请尽早接入 033[0m"
  exit 1
fi
}
