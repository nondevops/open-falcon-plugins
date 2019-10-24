# open-facon 常用插件监控脚本集合(全网最新并持续更新)

## 监控说明

``` text
部分脚本运行在有 相应服务 实例的虚拟机;
open-falcon-agent服务需要运行正常;
agent服务由于受puppet管理,读取并更新到open-falcon-agent.json hostname字段;
agent服务端口为11988;
使用plugin模式运行;
主机组务必要启用相关的插件目录;
部分监控为独立的模板和独立的主机组,如证书监控,根据自身的需求做相应的调整;
部分未出现的本项目中的脚本在使用时采用官方文档说明中的脚本,请自行访问并配置;
```

## 脚本介绍

``` bash
.
├── README.md # 本项目自述文件
├── cachecloud # cachecloud 监控脚本,如自身业务在使用cachecloud做缓存,参照此脚本配置;
│   └── README.md
├── cert # 证书过期 监控脚本;
│   ├── 60_cert_expire_time_monitor.py
│   └── 60_cert_expire_time_monitor.sh
├── domain # 域名过期 监控脚本;
│   └── 60_domain_expire_time_monitor.sh
├── haproxy # haproxy 监控脚本;
│   ├── 60_haproxy-monitor.py
│   └── README.md
├── hardware # 硬件 监控脚本;
│   ├── 60_hw_dell_monitor.py
│   ├── 60_raid_monitor.py
│   └── hwcheck-no-use.py
├── lvs # lvs 监控脚本;
│   └── 60_lvs_monitor.py
├── memcached # memcached 监控脚本;
│   ├── 60_memcached-monitor.py
│   └── README.md
├── mongodb # mongodb 监控脚本;
│   └── 60_mongodb_monitor.py
├── nginx # nginx 监控脚本;
│   ├── nginx-status-monitor
│   │   ├── 60_nginx-status-monitor.py
│   │   └── README.md
│   └── nginx-upstream-monitor
│       ├── 60_nginx_upstream-status-monitor.py
│       └── README.md
├── powerdns # powerdns 监控脚本;
│   └── 60_powerdns_monitor.py
├── rabbitmq # powrabbitmqerdns 监控脚本;
│   └── 60_rabbitmq_monitor.py
├── redis # redis 监控脚本;
│   └── 60_redis_monitor.py
├── squid # squid 监控脚本;
│   └── 60_squid_monitor.py
├── sys # 系统级 监控脚本;
│   ├── disk # 磁盘读写测试 监控脚本;
│   │   └── 60_mountpoint_rw_test.py
│   ├── mail # 邮件队列 监控脚本;
│   │   └── \ 60_mailqueue.py
│   ├── ntp # 时间同步 监控脚本;
│   │   └── 600_ntp_monitor.py
│   ├── ping # ping 监控脚本;
│   │   ├── 60_ping_cmdb_inner_instance_ip_monitor.sh
│   │   └── 60_ping_other_ip_monitor.py
│   └── proc-resource # 进程资源消耗 监控脚本;
│       └── 60_proc_resource_monitor.py
└── zookeeper # zookeeper 监控脚本;
    └── 60_zookeeper_monitor.py
```

## 克隆代码

``` bash
git clone https://github.com/nondevops/open-falcon-plugins.git
```

## 提交修改配置

``` text
由于puppet配置是通过git仓库管理, 需提交修改然后分发到相应的虚拟机才能生效,如未这样使用,请忽略此步骤
```

## open-falcon管理端启用该插件

``` text
根据自身的需求在相应的主机组启用该插件目录
```

## 检验数据上报情况

``` text
检查是否上报数据, 在dashboard搜索该机器,如过滤 nginx.conf 信息,如有数据,则表示采集上报成功
```

## 模板配置告警策略

``` text
根据自身的监控指标来设置
```

## 欢迎访问我的博客

``` bash
获得更多的技术体验
https://www.cqops.club
```
