"""
  Server Density Plugin
  Redis Server

  https://www.serverdensity.com/plugins/redis/
  https://github.com/serverdensity/sd-agent-plugins/


  Version: 1.0.0
"""

import json
import logging
import os
import platform
import sys
import time


class Redis(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()
        try:
            import redis
        except Exception:
            self.checks_logger.error(
                'Python Redis module not installed,' +
                'please install https://pypi.python.org/pypi/redis/')

        self.host = self.raw_config['Redis'].get('host', 'localhost')
        self.port = int(self.raw_config['Redis'].get('port', '6379'))
        self.dbs = self.raw_config['Redis'].get('dbs', ['0'])
        self.password = self.raw_config['Redis'].get('password', '')

    def run(self):
        import redis
        data = {}
        stats = None
        for db in self.dbs.split(','):
            redis_connection = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=int(db),
                password=self.password)
            stats = redis_connection.info()

        if not stats:
            return data

        for name, value in stats.iteritems():

            if name in ['used_memory_peak_human', 'used_memory_human']:
                value = float(value[0:-1])

            if name == 'role' and value == 'master':
                value = 1

            try:
                data[name] = float(value)
            except (ValueError, TypeError) as e:
                # some values are text rather numbers
                # fail and move on
                pass
        return data


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Redis': {
            'host': 'localhost',
            'port': '6379',
            'dbs': '0',
            'password': ''
        }
    }

    main_checks_logger = logging.getLogger('Redis')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    redis_check = Redis({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(redis_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
