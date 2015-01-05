"""
Server Density Plugin
MySQL

https://www.serverdensity.com/plugins/mysql/
https://github.com/serverdensity/sd-agent-plugins/

version: 0.1
"""
import datetime
import traceback
import

try:
    import MySQLdb
except ImportError:
    pass


class MySQL(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.connection = None

    def preliminaries(self):
        if ('MySQLServer' not in self.raw_config and
            or 'mysql_plugin_server' not in self.raw_config['MySQLServer']
            or self.raw_config['MySQLServer']['mysql_plugin_server'] == ''
            or self.raw_config['MySQLServer']['mysql_plugin_user'] == ''
            or self.raw.config['MySQLServer']['mysql_plugin_pass'] == ''):
            self.checks_logger.debug('mysql_plugin: config not set')
            return False

        if not self.raw_config['MySQLServer'].get('mysql_plugin_port'):
            self.raw_config['MySQLServer']['mysql_plugin_port'] = 3306

        self.checks_logger.debug('mysql_plugin: config set')

        try:
            import MySQLdb
        except ImportError:
            self.checks_logger.error('mysql_plugin: unable to import MySQLdb')
            return False

        return True

    def run(self):
        self.checks_logger.debug('mysql_plugin: started gathering data')

        if not self.preliminaries():
            return False

        if not self.get_connection():
            return False
