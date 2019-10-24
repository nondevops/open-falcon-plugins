#!/usr/bin/env python

import threading
import elasticsearch
import json
import time
from datetime import datetime
import requests


class EsMetrics(threading.Thread):
    status_map = {
        'green': 0,
        'yellow': 1,
        'red': 2
    }

    def __init__(self, falcon_conf, es_conf):
        self.falcon_conf = falcon_conf
        self.es_conf = es_conf
        # Assign default conf
        if 'test_run' not in self.falcon_conf:
            self.falcon_conf['test_run'] = False
        if 'step' not in self.falcon_conf:
            self.falcon_conf['step'] = 60

        self.index_metrics = {
            'search': ['query_total', 'query_time_in_millis', 'query_current', 'fetch_total', 'fetch_time_in_millis', 'fetch_current'],
            'indexing': ['index_total', 'index_current', 'index_time_in_millis', 'delete_total', 'delete_current', 'delete_time_in_millis'],
            'docs': ['count', 'deleted'],
            'store': ['size_in_bytes', 'throttle_time_in_millis']
        }
        self.cluster_metrics = ['status', 'number_of_nodes', 'number_of_data_nodes', 'active_primary_shards', 'active_shards', 'unassigned_shards']
        self.counter_keywords = ['query_total', 'query_time_in_millis',
            'fetch_total', 'fetch_time_in_millis',
            'index_total', 'index_time_in_millis', 
            'delete_total', 'delete_time_in_millis']
        super(EsMetrics, self).__init__(None, name=self.es_conf['endpoint'])
        self.setDaemon(False)

    def run(self):
        try:
            self.es = elasticsearch.Elasticsearch([self.es_conf['url']])
            falcon_metrics = []
            # Statistics
            timestamp = int(time.time())
            nodes_stats = self.es.nodes.stats()
            cluster_health = self.es.cluster.health()
            keyword_metric = {}
            for node in nodes_stats['nodes']:
                index_stats = nodes_stats['nodes'][node]['indices']
                for type in self.index_metrics:
                    for keyword in self.index_metrics[type]:
                        if keyword not in keyword_metric:
                            keyword_metric[keyword] = 0
                        keyword_metric[keyword] += index_stats[type][keyword]
            for keyword in self.cluster_metrics:
                if keyword == 'status':
                    keyword_metric[keyword] = self.status_map[cluster_health[keyword]]
                else:
                    keyword_metric[keyword] = cluster_health[keyword]
            for keyword in keyword_metric:
                falcon_metric = {
                    'counterType': 'COUNTER' if keyword in self.counter_keywords else 'GAUGE',
                    'metric': "es." + keyword,
                    'endpoint': self.es_conf['endpoint'],
                    'timestamp': timestamp,
                    'step': self.falcon_conf['step'],
                    'tags': 'n=' + nodes_stats['cluster_name'],
                    'value': keyword_metric[keyword]
                }
                falcon_metrics.append(falcon_metric)
            if self.falcon_conf['test_run']:
                print json.dumps(falcon_metrics)
            else:
                req = requests.post(self.falcon_conf['push_url'], data=json.dumps(falcon_metrics))
                print datetime.now(), "INFO: [%s]" % self.es_conf['endpoint'], "[%s]" % self.falcon_conf['push_url'], req.text
        except Exception as e:
            if self.falcon_conf['test_run']:
                raise
            else:
                print datetime.now(), "ERROR: [%s]" % self.es_conf['endpoint'], e
