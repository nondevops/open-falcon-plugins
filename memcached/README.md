# open-falcon memcached监控

## 监控原因

``` text
无法掌握memcached服务的消耗情况,如缓存命中数等指标
```

## 监控说明

``` text
该脚本运行在有 memcached 实例的虚拟机;
open-falcon-agent服务运行正常;
agent服务由于受puppet管理,读取并更新到open-falcon-agent.json hostname字段;
agent服务端口为11988;
使用plugin模式运行;
```

## 克隆代码

``` bash
git clone https://github.com/nondevops/open-falcon-memcached.git
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
检查是否上报数据, 在dashboard搜索该机器,如过滤 memcached 信息,如有数据,则表示采集上报成功
```

## 模板配置告警策略

``` text
根据自身的监控指标来设置
```
