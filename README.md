# open-facon 常用插件监控脚本集合(全网最新并持续更新)

## 该仓库的产生背景

``` text
2019年重构了监控系统使用open-falcon来代替zabbix继续提供监控服务,zabbix很多脚本无法在open-falcon直接使用;
鉴于基础设施非常复杂,结合实际业务需求特记录常用的监控对象采集脚本,避免大家在用open-falcon时少走一些弯路,不重复造轮子...
```

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
cachecloud # cachecloud 监控,soho开源的redis管理平台
ceph # ceph 监控
cert # 证书过期 监控
domain # 域名过期 监控
es # es 监控
hadoop # hadoop 监控
haproxy # haproxy 监控
hardware # hardware 监控
lvs # lvs 监控
memcached # memcached 监控
mongodb # mongodb 监控
nginx # nginx 监控
powerdns # powerdns 监控
public-cloud # 公有云 监控,如ELB数据
rabbitmq # rabbitmq 监控
redis # redis 监控
solr # solr 监控
squid # squid 监控
sys # 系统级 监控
zookeeper # zookeeper 监控
.....(脚本太多了直接clone下来慢慢看吧)


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
## 意见和交流
```
如对脚本有疑问或有错误,欢迎提PR,大家共同维护
```

## 注意
```
如使用脚本产生了生产环境故障,本人不负任何责任哈,请在测试环境充分测试后上线.有些场景可能脚本没有考虑到,请多理解
特别说明一下,请尊重劳动成果,来之不易,能给开源事业做贡献已经做了很大牺牲,希望广大用户不喜勿喷...
```

## 欢迎访问我的博客

``` bash
获得更多的技术体验
https://www.cqops.club
```
