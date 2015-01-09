"""
Server Density plugin
MySQL

https://www.serverdensity.com/plugins/mysql/
https://github.com/serverdensity/sd-agent-plugins/

version: 0.1
"""
import traceback
import re

try:
    import MySQLdb
except ImportError:
    pass

# com commands.
COMMANDS = [
    'Com_show_status',
    'Com_select',
    'Com_delete',
    'Com_update'
]

class MySQL(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.connection = None
        self.datastore = {}

    def version_is_above_5(self, status):
        if (int(status['version'][0]) >= 5
                and int(status['version'][2]) >= 2):
            return True
        else:
            return False

    def get_db_results(self, db, query):
        cursor = db.cursor()
        try:
            cursor.execute(query)
            results = float(cursor.fetchone()[1])
        except ValueError:
            cursor.execute(query)
            results = cursor.fetchone()[1]
        return results

    def calculate_per_s(self, command, result):
        if (not self.datastore.get(command)
                and self.datastore.get(command) != 0):
            self.checks_logger.debug(
                'mysql: Datastore unset for '
                '{}, storing for first time'.format(command))
            self.datastore[command] = result
            com_per_s = 0
        else:
            com_per_s = (result - self.datastore[command]) / 60
            if com_per_s < 0:
                com_per_s = 0
            self.datastore[command] = result
        return com_per_s

    def preliminaries(self):
        if ('MySQLServer' not in self.raw_config
                and 'mysql_server' not in self.raw_config['MySQLServer']
                or self.raw_config['MySQLServer']['mysql_server'] == ''
                or self.raw_config['MySQLServer']['mysql_user'] == ''
                or self.raw_config['MySQLServer']['mysql_pass'] == ''):
            self.checks_logger.debug('mysql: config not set')
            return False

        if not self.raw_config['MySQLServer'].get('mysql_port'):
            self.raw_config['MySQLServer']['mysql_port'] = "3306"

        self.checks_logger.debug('mysql: config set')

        try:
            import MySQLdb
        except ImportError:
            self.checks_logger.error('mysql: unable to import MySQLdb')
            return False

        # Note, code here doesn't really make sense. See what I copied.
        if not self.raw_config['MySQLServer'].get('mysql_port'):
            # Connect
            try:
                MySQLdb.connect(
                    host=self.raw_config['MySQLServer']['mysql_server'],
                    user=self.raw_config['MySQLServer']['mysql_user'],
                    passw=self.raw_config['MySQLServer']['mysql_pass'],
                    port=int(self.raw_config['MySQLServer']['mysql_port'])
                    )
            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    "mysql: MySQL connection error: {}".format(message))
                return False
        else:
            # Connect
            try:
                MySQLdb.connect(
                    host='localhost',
                    user=self.raw_config['MySQLServer']['mysql_user'],
                    passwd=self.raw_config['MySQLServer']['mysql_pass'],
                    port=int(self.raw_config['MySQLServer']['mysql_port']))
            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL connection error: {}'.format(message)
                    )
                return False
        return True

    def get_connection(self):
        try:
            # connection
            db = MySQLdb.connect(
                host=self.raw_config['MySQLServer']['mysql_server'],
                user=self.raw_config['MySQLServer']['mysql_user'],
                passwd=self.raw_config['MySQLServer']['mysql_pass'],
                port=int(self.raw_config['MySQLServer']['mysql_port'])
                )
            self.connection = db
            # note, how do I take into account the socket?
        except Exception:
            self.checks_logger.error(
                'Unable to connect to MySQL server {0} - Exception: {1}'.format(
                    self.config_raw['MySQLServer']['mysql_server'],
                    traceback.format_exc())
                )
            return False
        return True

    def run(self):
        self.checks_logger.debug('mysql: started gathering data')
        if not self.preliminaries():
            return False

        if not self.get_connection():
            return False

        try:
            db = self.connection

            # setup
            status = {}

            # Get MySQL version
            try:
                self.checks_logger.debug('mysql: getting mysqlversion')

                cursor = db.cursor()
                cursor.execute('SELECT VERSION()')
                result = cursor.fetchone()

                version = result[0].split('-')
                # Case 31237. Might include a description e.g. 4.1.26-log.
                # See http://dev.mysql.com/doc/refman/4.1/en/information-functions.html#function_version
                version = version[0].split('.')

                status['version'] = []

                for version_item in version:
                    number = re.match('([0-9]+)', version_item)
                    number = number.group(0)
                    status['version'].append(number)

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting version: {}'.format(
                        message)
                    )
                return False

            # get Uptime
            try:
                status['Uptime'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Uptime"'
                )
            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting Uptime = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug('mysql: getting Uptime - done')

            # Slow queries
            # Determine query depending on version. For 5.02 and above we
            # need the GLOBAL keyword (case 31015)
            # note, update with slow queries store. making it per second?
            # ask jordi about that.
            try:
                if self.version_is_above_5(status):
                    query = 'SHOW GLOBAL STATUS LIKE "Slow_queries"'
                else:
                    query = 'SHOW STATUS LIKE "Slow_queries'

                status['Slow queries'] = self.get_db_results(db, query)
            except MySQLdb.OperationalError as message:
                self.checks_logger(
                    'mysql: MySQL query error when getting Slow_queries = {}'.format(
                        message)
                    )
                return False
            self.checks_logger.debug('mysql: getting Slow_queries - done')

            # QPS - Queries per second.
            try:
                if self.version_is_above_5(status):
                    query = 'SHOW GLOBAL STATUS LIKE "Queries"'
                else:
                    query = 'SHOW STATUS LIKE "Queries"'

                qps = self.calculate_per_s('qps', self.get_db_results(
                    db, query))
                status['Queries per second'] = qps

            except MySQLdb.OperationalError as message:
                self.checks_logger.debug(
                    'mysql: MySQL query error when getting QPS = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug('mysql: getting QPS - done')

            # Connection pool
            try:
                status['threads_connected'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Threads_connected"')

                status['threads_running'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Threads_running"')

                status['max_connections'] = self.get_db_results(
                    db, 'SHOW VARIABLES LIKE "max_connections"')

                status['max_used_connections'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Max_used_connections"')

                status['Connection usage %'] = (
                    (status['threads_running']/status['max_connections'])*100
                )

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting Threads_connected: {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug('mysql: getting connections - done')

            # Buffer pool
            try:

                status['buffer_pool_pages_total'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Innodb_buffer_pool_pages_total"')

                status['buffer_pool_pages_free'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Innodb_buffer_pool_pages_free"')

                status['buffer_pool_pages_dirty'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Innodb_buffer_pool_pages_dirty"')

                status['buffer_pool_pages_data'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Innodb_buffer_pool_pages_data"')

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting Buffer pool pages = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug('mysql: getting buffer pool - done')

            # Query cache items
            try:
                status['qcache_hits'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Qcache_hits"')

                qcache_ps = self.calculate_per_s('qcache_ps', status[
                    'qcache_hits'])
                status['qcache_hits/s'] = qcache_ps
                # NOTE: needs cache hits per second. How does that relate
                # to above?

                status['qcache_free_memory'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Qcache_free_memory"')

                status['qcache_not_cached'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Qcache_not_cached"')

                status['qcache_in_cache'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Qcache_queries_in_cache"')

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting Qcache data = {}'.format(
                        message))
                return False

            self.checks_logger.debug('mysql: getting Qcache data - done')

            # writes, reads, transactions
            try:
                # writes
                insert = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_insert"')

                replace = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_replace"')

                update = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_update"')

                delete = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_delete"')

                writes = insert + replace + update + delete
                status['Writes/s'] = self.calculate_per_s('writes', writes)

                # reads
                select = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_select"')

                reads = select + status['qcache_hits']
                status['Reads/s'] = self.calculate_per_s('reads', reads)

                # read write ratio
                try:
                    status['RW ratio'] = reads/writes
                except ZeroDivisionError:
                    status['RW ratio'] = 0

                # transactions
                commit = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_commit"')

                rollback = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Com_rollback"')

                transactions = commit + rollback
                status['Transactions/s'] = self.calculate_per_s(
                    'transactions', transactions)

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting writes,'
                    ' reads and transactions = {}'.format(
                        message)
                )
                return False

            # Aborted connections and clients
            try:
                status['aborted_clients'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Aborted_clients"')

                status['aborted_connects'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Aborted_connects"')

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting aborted items = {}'.format(
                        message)
                )
                return False

            self.checks_logger.debug(
                'mysql: getting aborted connections - done')

            # Replication - seconds behind master
            # note, is it enough? compared to old code?
            if self.raw_config['MySQLServer'].get('mysql_slave') == 'true':
                try:
                    status['seconds_behind_master'] = self.get_db_results(
                        db, 'SHOW SLAVE STATUS LIKE "Seconds_Behind_Master"')

                except MySQLdb.OperationalError as message:
                    self.checks_logger.error(
                        'mysql: MySQL query error when getting aborted items = {}'.format(
                            message)
                    )
                self.checks_logger(
                    'mysql: getting slave status data - done')
            else:
                pass

            # Created temporary tables in memory and on disk
            try:
                if self.version_is_above_5(status):
                    query = 'SHOW GLOBAL STATUS LIKE "Created_tmp_tables"'
                else:
                    query = 'SHOW STATUS LIKE "Created_tmp_tables"'
                status['created tmp tables'] = self.get_db_results(
                    db, query)

                if self.version_is_above_5(status):
                    query = 'SHOW GLOBAL STATUS LIKE "Created_tmp_disk_tables"'
                else:
                    query = 'SHOW STATUS LIKE "Created_tmp_disk_tables"'
                status['created tmp tables on disk'] = self.get_db_results(
                    db, query)

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting temp tables = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug(
                'mysql: getting temporary tables data - done')

            # select_full_join
            try:
                if self.version_is_above_5(status):
                    query = 'SHOW GLOBAL STATUS LIKE "Select_full_join"'
                else:
                    query = 'SHOW STATUS LIKE "Select_full_join"'
                status['select_full_join'] = self.get_db_results(
                    db, query)

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting select full join = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug('mysql: getting select_full_join - done')

            # slave_running
            try:
                result = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Slave_running"')
                if result == 'OFF':
                    result = 0
                else:
                    result = 1
                status['slave_running'] = result
            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting slave_running = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug(
                'mysql: getting slave_running - done')

            # open files
            try:
                status['open_files'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Open_files"')
            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting open files = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug('mysql: getting open_files - done')

            # table_locks_waited
            try:
                status['table_locks_waited'] = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Table_locks_waited"')
            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting table locks waited = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug(
                'mysql: getting table_locks_waited - done')

            # checkpoint age
            try:
                cursor = db.cursor()
                cursor.execute('SHOW ENGINE INNODB STATUS')
                results = cursor.fetchone()[2]

                log_loci = results.find('Log sequence number')
                checkpoint_loci = results.find('Last checkpoint at')

                log_nr = int(re.search(r'\d+', results[log_loci:]).group(0))
                cp_nr = int(re.search(r'\d+', results[checkpoint_loci:]).group(0))

                cp_age = cp_nr - log_nr
                status['Checkpoint age'] = cp_age

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting checkpoint age = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug(
                'mysql: getting checkpoint age - done')

            try:
                # Key cache hit ratio
                # http://www.percona.com/blog/2010/02/28/why-you-should-ignore-mysqls-key-cache-hit-ratio/
                key_read = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Key_reads"')

                key_requests = self.get_db_results(
                    db, 'SHOW STATUS LIKE "Key_read_requests"')

                status['Key cache hit ratio'] = (
                    1 - (key_read/key_requests))*100

                status['Key reads/s'] = self.calculate_per_s(
                    "Key_reads", key_read)

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting key cache = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug(
                'mysql: getting key cache hit ratio - done')

            # com commands per second
            try:
                cursor = db.cursor()
                for command in COMMANDS:
                    if self.version_is_above_5(status):
                        query = 'SHOW GLOBAL STATUS LIKE "{}"'.format(command)
                    else:
                        query = 'SHOW STATUS LIKE "{}"'.format(command)
                    com_per_s = self.calculate_per_s(
                        command, self.get_db_results(db, query)
                    )
                    status[command.replace('_', ' ')+'/s'] = com_per_s

            except MySQLdb.OperationalError as message:
                self.checks_logger.error(
                    'mysql: MySQL query error when getting com commands = {}'.format(
                        message)
                )
                return False
            self.checks_logger.debug(
                'mysql: getting com_commands - done')

        except Exception:
            self.checks_logger.error(
                'mysql: unable to get data from MySQL - '
                'Exception: {}'.format(traceback.format_exc())
                )

        self.checks_logger.debug('mysql: completed, returning')
        return status

if __name__ == "__main__":
    """Standalone test"""

    import logging
    import sys
    import json
    import time
    host = 'localhost'
    port = '3306'

    raw_agent_config = {
        'MySQLServer': {
            'mysql_server': host,
            'mysql_port': port,
            'mysql_user': 'jonathan',
            'mysql_pass': 'password'
        }
    }

    main_checks_logger = logging.getLogger('MySQLplugin')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    mysql_check = MySQL({}, main_checks_logger, raw_agent_config)
    while True:
        try:
            result = mysql_check.run()
            print(json.dumps(result, indent=4, sort_keys=True))
        except:
            main_checks_logger.exception("Unhandled Exception")
        finally:
            time.sleep(60)
