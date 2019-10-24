#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
import time
import socket
import subprocess


ENDPOINT = socket.getfqdn()
STEP = 60
TYPE_GAUGE = 'GAUGE'
TYPE_COUNTER = 'COUNTER'
KAFKA_HOME = '/opt/prismcdn/kafka'
JMX_CMD = ' '.join(['bin/kafka-run-class.sh', 'kafka.tools.JmxTool',
        '--object-name', '"kafka.*:type=*,name=*"',
        '--object-name', '"kafka.network:type=*,name=*,request=*"',
        '--object-name', '"kafka.server:type=*"',
        '--object-name', '"kafka.server:type=ReplicaFetcherManager,name=MaxLag,clientId=Replica"',
        ])


OBJECT_NAMES = {
        'kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions:Value': 'kafka.replica.UnderReplicatedPartitions',
        'kafka.server:type=ReplicaManager,name=IsrShrinksPerSec:Count': 'kafka.replica.IsrShrinksPerSec.count',
        'kafka.server:type=ReplicaManager,name=IsrExpandsPerSec:Count': 'kafka.replica.IsrExpandsPerSec.count',
        'kafka.server:type=ReplicaFetcherManager,name=MaxLag,clientId=Replica:Value': 'kafka.replica.MaxLag',
        'kafka.controller:type=KafkaController,name=ActiveControllerCount:Value': 'kafka.controller.ActiveControllerCount',
        'kafka.controller:type=KafkaController,name=OfflinePartitionsCount:Value': 'kafka.controller.OfflinePartitionsCount',
        'kafka.controller:type=ControllerStats,name=LeaderElectionRateAndTimeMs:Count': 'kafka.controller.LeaderElectionRateAndTimeMs.count',
        'kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec:Count': 'kafka.controller.UncleanLeaderElectionsPerSec.count',
        'kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce:Count': 'kafka.RequestMetrics.TotalTimeMs.Produce.count',
        'kafka.network:type=RequestMetrics,name=TotalTimeMs,request=FetchConsumer:Count': 'kafka.RequestMetrics.TotalTimeMs.FetchConsumer.count',
        'kafka.network:type=RequestMetrics,name=TotalTimeMs,request=FetchFollower:Count': 'kafka.RequestMetrics.TotalTimeMs.FetchFollower.count',
        # 'kafka.server:type=ProducerRequestPurgatory,name=PurgatorySize',
        # 'kafka.server:type=FetchRequestPurgatory,name=PurgatorySize',
        'kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec:Count': 'kafka.BrokerTopicMetrics.BytesInPerSec.count',
        'kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec:Count': 'kafka.BrokerTopicMetrics.BytesOutPerSec.count',
        'kafka.server:type=Fetch:queue-size': 'kafka.server.fetch.queue.size',
        'kafka.server:type=Produce:queue-size': 'kafka.server.produce.queue.size',
        }

class KafkaJMXMetrics(object):
    def run(self):
        data = []
        for item in self._query_jmx():
            data.append(item)
        print(json.dumps(data))

    def _query_jmx(self):
        p = subprocess.Popen(JMX_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=KAFKA_HOME, shell=True)
        try:
            header = p.stdout.readline()
            row = p.stdout.readline()
        finally:
            p.terminate()
        metric_ptn = re.compile('"([^"]+)"')
        object_names = metric_ptn.findall(header)
        records = row.split(',')
        for obj_name, metric in OBJECT_NAMES.iteritems():
            value = records[object_names.index(obj_name)]
            yield self._build_metric(metric, value, obj_name.endswith(':Count') and TYPE_COUNTER or TYPE_GAUGE)

    def _build_metric(self, metric, value, counter_type=TYPE_GAUGE, tags=''):
        return {
                'metric': metric,
                'endpoint': ENDPOINT,
                'timestamp': int(time.time()),
                'step': STEP,
                'value': value,
                'counterType': counter_type,
                'tags': tags
                }

KafkaJMXMetrics().run()