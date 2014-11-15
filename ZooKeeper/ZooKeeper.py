"""
Server Density Plugin
Mongodb

https://www.serverdensity.com/plugins/ZooKeeper/
https://github.com/serverdensity/sd-agent-plugins/


Version: 1.0.0
"""

import socket
import traceback


class ZooKeeper(object):
    """Plugin class to manage extracting the data from Mongo
       for the sd-agent.
    """

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.zookeeper_commands = [
			'conf',
			'ruok',
			'srvr',
		]

    def run(self):
        data = {}
        self.checks_logger.debug('ZooKeeper_plugin: started gathering data')

        for command in self.zookeeper_commands:
           s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           s.connect(
               (self.raw_config['ZooKeeper']['host'], 
                int(self.raw_config['ZooKeeper']['port']))
           )
           s.sendall(command)
           reply = s.recv(1024)
           if command == 'conf':
               data = self.convert_conf(data, reply)
           elif command == 'ruok':
               data = self.convert_ruok(data, reply)
           elif command == 'srvr':
               data = self.convert_srvr(data, reply)
           
        self.checks_logger.debug('ZooKeeper_plugin: completed, returning')

        return data

  
    def convert_conf(self, data, reply):
        """
        clientPort=2181
        dataDir=/usr/local/var/run/zookeeper/data/version-2
        dataLogDir=/usr/local/var/run/zookeeper/data/version-2
        tickTime=2000
        maxClientCnxns=10
        minSessionTimeout=4000
        maxSessionTimeout=40000
        serverId=0
        """

        for line in reply.split('\n'):
            if not line:
                continue
            key, value = line.split('=')
            if key in ['dataDir', 'dataLogDir']:
                continue
            data[key] = int(value)
        return data 

    def convert_ruok(self, data, reply):
        if reply == 'imok':
            data['imok'] = 1
        else:
            data['imok'] = 0
        return data

    def convert_srvr(self, data, reply):
        """
        Latency min/avg/max: 0/0/0
        Received: 52
        Sent: 51
        Outstanding: 0
        Zxid: 0x0
        Mode: standalone
        Node count: 4
        """

        for line in reply.split('\n'):
            if not line or line.startswith('Zookeeper version'):
                continue
            print line
            key, value = line.split(':')

            if key in ['Mode', 'Zxid']:
                continue

            if key.startswith('Latency min/avg/max'):
                data['latency min'] = int(value.split('/')[0])
                data['latency avg'] = int(value.split('/')[1])
                data['latency max'] = int(value.split('/')[2])
            else:
                data[key] = int(value.strip())
        return data

if __name__ == "__main__":
    """Standalone test
    """

    import logging
    import sys
    import json
    import time
    host = '127.0.0.1'
    port = 2181

    raw_agent_config = {
        'ZooKeeper': {
            'host': host,
            'port': port
        }
    }

    main_checks_logger = logging.getLogger('ZooKeeperPlugin')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    zookeeper_check = ZooKeeper({}, main_checks_logger, raw_agent_config)
    while True:
        try:
            result = zookeeper_check.run()
            print json.dumps(result, indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
