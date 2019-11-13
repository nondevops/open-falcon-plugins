#! /usr/bin/env python

import sys
import socket
import logging
import re
import subprocess
import json
import time
import urllib2, base64

from StringIO import StringIO
from optparse import OptionParser, OptionGroup

__version__ = (0, 1, 0)

log = logging.getLogger()
logging.basicConfig(level=logging.ERROR)

class ZooKeeperServer(object):

    def __init__(self, host='localhost', port='2181', timeout=1):
        self._address = (host, int(port))
        self._timeout = timeout

    def get_stats(self):
        """ Get ZooKeeper server stats as a map """
        data = self._send_cmd('mntr')
        if data:
            return self._parse(data)
        else:
            data = self._send_cmd('stat')
            return self._parse_stat(data)

    def _create_socket(self):
        return socket.socket()

    def _send_cmd(self, cmd):
        """ Send a 4letter word command to the server """
        s = self._create_socket()
        s.settimeout(self._timeout)

        s.connect(self._address)
        s.send(cmd)

        data = s.recv(2048)
        s.close()

        return data

    def _parse(self, data):
        """ Parse the output from the 'mntr' 4letter word command """
        h = StringIO(data)
        
        result = {}
        for line in h.readlines():
            try:
                key, value = self._parse_line(line)
                result[key] = value
            except ValueError:
                pass # ignore broken lines

        return result

    def _parse_stat(self, data):
        """ Parse the output from the 'stat' 4letter word command """
        h = StringIO(data)

        result = {}
        
        version = h.readline()
        if version:
            result['zk_version'] = version[version.index(':')+1:].strip()

        # skip all lines until we find the empty one
        while h.readline().strip(): pass

        for line in h.readlines():
            m = re.match('Latency min/avg/max: (\d+)/(\d+)/(\d+)', line)
            if m is not None:
                result['zk_min_latency'] = int(m.group(1))
                result['zk_avg_latency'] = int(m.group(2))
                result['zk_max_latency'] = int(m.group(3))
                continue

            m = re.match('Received: (\d+)', line)
            if m is not None:
                result['zk_packets_received'] = int(m.group(1))
                continue

            m = re.match('Sent: (\d+)', line)
            if m is not None:
                result['zk_packets_sent'] = int(m.group(1))
                continue

            m = re.match('Outstanding: (\d+)', line)
            if m is not None:
                result['zk_outstanding_requests'] = int(m.group(1))
                continue

            m = re.match('Mode: (.*)', line)
            if m is not None:
                result['zk_server_state'] = m.group(1)
                continue

            m = re.match('Node count: (\d+)', line)
            if m is not None:
                result['zk_znode_count'] = int(m.group(1))
                continue

        return result 

    def _parse_line(self, line):
        try:
            key, value = map(str.strip, line.split('\t'))
        except ValueError:
            raise ValueError('Found invalid line: %s' % line)

        if not key:
            raise ValueError('The key is mandatory and should not be empty')

        try:
            value = int(value)
        except (TypeError, ValueError):
            pass

        return key, value

def main():
    #servers = [['floor3_test', '127.0.0.1', 2181]]
    opts, args = parse_cli()
    cluster_stats = get_cluster_stats(opts.servers)
    dump_stats(cluster_stats)
    for endpoint, stats in cluster_stats.items():
        metrics = stats_to_metrics(endpoint, stats)
        print json.dumps(metrics, sort_keys=True,indent=4)
        #push_metrics(metrics)
    
# def push_metrics(metrics):
#     method = "POST"
#     handler = urllib2.HTTPHandler()
#     opener = urllib2.build_opener(handler)
#     url = 'http://127.0.0.1:1988/v1/push'
#     request = urllib2.Request(url, data=json.dumps(metrics) )
#     request.add_header("Content-Type",'application/json')
#     request.get_method = lambda: method
#     try:
#         connection = opener.open(request)
#     except urllib2.HTTPError,e:
#         connection = e

#     # check. Substitute with appropriate HTTP code.
#     if connection.code == 200:
#         print connection.read()
#     else:
#         print '{"err":1,"msg":"%s"}' % connection 

def stats_to_metrics(endpoint, stats):
    p = []
    metric = "zookeeper"
    timestamp = int(time.time())
    step = 60
    monit_keys = [
        ('zk_avg_latency','GAUGE'), 
        ('zk_max_latency','GAUGE'), 
        ('zk_min_latency','GAUGE'),
        ('zk_packets_received','COUNTER'),
        ('zk_packets_sent','COUNTER'),
        ('zk_num_alive_connections','GAUGE'),
        ('zk_outstanding_requests','GAUGE'),
        ('zk_znode_count','GAUGE'),
        ('zk_watch_count','GAUGE'),
        ('zk_ephemerals_count','GAUGE'),
        ('zk_approximate_data_size','GAUGE'),
        ('zk_open_file_descriptor_count','GAUGE'),
        ('zk_max_file_descriptor_count','GAUGE'),
	('zk_pending_syncs','GAUGE'),
	('zk_followers','GAUGE'),
    ]
    for key,vtype in monit_keys:
        try:
            value = int(stats[key])
        except:
            continue
        i = {
            'Metric': '%s.%s' % (metric, key),
            'Endpoint': endpoint,
            'Timestamp': timestamp,
            'Step': step,
            'Value': value,
            'CounterType': vtype,
            'TAGS': ''
        }
        p.append(i)
    return p


def dump_stats(cluster_stats):
    """ Dump cluster statistics in an user friendly format """
    for server, stats in cluster_stats.items():
        print 'Server:', server

        for key, value in stats.items():
            print "%30s" % key, ' ', value
        print

def get_cluster_stats(servers):
    """ Get stats for all the servers in the cluster """
    stats = {}
    for endpoint, host, port in servers:
        try:
            zk = ZooKeeperServer(host, port)
            stats[endpoint] = zk.get_stats()

        except socket.error, e:
            # ignore because the cluster can still work even 
            # if some servers fail completely

            # this error should be also visible in a variable
            # exposed by the server in the statistics

            logging.info('unable to connect to server '\
                '"%s" on port "%s"' % (host, port))

    return stats

def get_version():
    return '.'.join(map(str, __version__))

def parse_cli():
    parser = OptionParser(usage='./60_zk_monitor_use.py <options>', version=get_version())

    parser.add_option('-s', '--servers', dest='servers', 
        help='a list of SERVERS', metavar='SERVERS')

    opts, args = parser.parse_args()

    if opts.servers is None:
        parser.error('The list of servers is mandatory')

    opts.servers = [s.split(':') for s in opts.servers.split(',')]

    return (opts, args)

if __name__ == '__main__':
    main()