#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import socket
from kafka.client import KafkaClient
from kafka.producer import KafkaProducer
from kafka.consumer import KafkaConsumer


ENDPOINT = socket.getfqdn()
SERVER = '%s:9092' % ENDPOINT
STEP = 300
TYPE_GAUGE = 'GAUGE'


class KafkaMetrics(object):
    def __init__(self):
        self.client = KafkaClient(bootstrap_servers=SERVER)
        self.cluster = self.client.cluster
        self.producer = KafkaProducer(bootstrap_servers=SERVER)
        self.consumer = KafkaConsumer(bootstrap_servers=SERVER)

    def run(self):
        data = []
        for collector in [getattr(self, f) for f in dir(self) if f.startswith('get_')]:
            items = collector()
            if isinstance(items, dict):
                data.append(items)
            else: # iterator
                for item in items:
                    data.append(item)

        print(json.dumps(data))

    def get_brokers_total(self):
        metric = 'kafka.brokers.total'

        return self._build_metric(metric, len(self.cluster.brokers()))

    def get_topics_total(self):
        metric = 'kafka.topics.total'

        return self._build_metric(metric, len(self.cluster.topics()))

    def get_consumer_metrics(self):
        metrics = self.consumer.metrics()
        # 'consumer-metrics': {'connection-close-rate': 0.0,
        # 'connection-count': 1.0,
        # 'connection-creation-rate': 0.0,
        # 'incoming-byte-rate': 0.0,
        # 'io-ratio': 0.0,
        # 'io-time-ns-avg': 0.0,
        # 'io-wait-ratio': 0.0,
        # 'io-wait-time-ns-avg': 0.0,
        # 'network-io-rate': 0.0,
        # 'outgoing-byte-rate': 0.0,
        # 'request-latency-avg': 0.0,
        # 'request-latency-max': -inf,
        # 'request-rate': 0.0,
        # 'request-size-avg': 0.0,
        # 'request-size-max': -inf,
        # 'response-rate': 0.0,
        # 'select-rate': 0.0},
        for k, v in metrics.get('consumer-metrics', {}).iteritems():
            metric = 'kafka.consumer.' + k.replace('-', '_')
            value = v > 0 and v or 0.0
            yield self._build_metric(metric, value)

    def get_producer_metrics(self):
        metrics = self.producer.metrics()
        # 'producer-metrics': {'batch-size-avg': 0.0,
        # 'batch-size-max': -inf,
        # 'bufferpool-wait-ratio': 0.0,
        # 'byte-rate': 0.0,
        # 'compression-rate-avg': 0.0,
        # 'connection-close-rate': 0.0,
        # 'connection-count': 1.0,
        # 'connection-creation-rate': 0.0,
        # 'incoming-byte-rate': 0.0,
        # 'io-ratio': 7.385267125376526e-06,
        # 'io-time-ns-avg': 136017.7993774414,
        # 'io-wait-ratio': 1.6298991923996782,
        # 'io-wait-time-ns-avg': 30019315600.395203,
        # 'metadata-age': 186.95360986328126,
        # 'network-io-rate': 0.0,
        # 'outgoing-byte-rate': 0.0,
        # 'produce-throttle-time-avg': 0.0,
        # 'produce-throttle-time-max': -inf,
        # 'record-error-rate': 0.0,
        # 'record-queue-time-avg': 0.0,
        # 'record-queue-time-max': -inf,
        # 'record-retry-rate': 0.0,
        # 'record-send-rate': 0.0,
        # 'record-size-avg': 0.0,
        # 'record-size-max': -inf,
        # 'records-per-request-avg': 0.0,
        # 'request-latency-avg': 0.0,
        # 'request-latency-max': -inf,
        # 'request-rate': 0.0,
        # 'request-size-avg': 0.0,
        # 'request-size-max': -inf,
        # 'requests-in-flight': 0.0,
        # 'response-rate': 0.0,
        # 'select-rate': 0.054297494580905235},
        for k, v in metrics.get('producer-metrics', {}).iteritems():
            metric = 'kafka.producer.' + k.replace('-', '_')
            value = v > 0 and v or 0.0
            yield self._build_metric(metric, value)

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


KafkaMetrics().run()