# es-open-falcon

ElasticSearch Monitor Script for Open Falcon

### Step 1: Edit conf

Rename `es-open-falcon.yml.default` to `es-open-falcon.yml`, then edit the file, and add your es servers.

```yml
falcon:
    push_url: http://127.0.0.1:11988/v1/push
    step: 60

# Elasticsearch clusters
es-clusters:
    - {endpoint: "localhost", url: "http://127.0.0.1:9200"}

```

### Step 2: Add the monitor script to crontab

```
$ crontab -l
*/1 * * * * cd /path/to/es-open-falcon && python -u ./bin/es-falcon.py >> es-open-falcon.log 2>&1
```

# es-open-falcon

用于 Open Falcon 的 ElasticSearch 监控采集脚本

### 第一步：编辑配置文件

将 `es-open-falcon.yml.default` 重命名为 `es-open-falcon.yml`，然后编辑这个文件，添加你要监控的 ElasticSearch 服务器信息。

```yml
falcon:
    push_url: http://127.0.0.1:11988/v1/push
    step: 60

# Elasticsearch clusters
es-clusters:
    - {endpoint: "localhost", url: "http://127.0.0.1:9200"}

```

### 第二步：将监控脚本添加到 crontab 中定时执行

```
$ crontab -l
*/1 * * * * cd /path/to/es-open-falcon && python -u ./bin/es-falcon.py >> es-open-falcon.log 2>&1
```
