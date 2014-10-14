#
# Server Density Plugin
# mongodb
#
# https://www.serverdensity.com/plugins/mongodb/
# https://github.com/serverdensity/sd-agent-plugins/

#
# Version: 0.2.0
#

import collections
import datetime
import traceback


try:
    import pymongo
    from pymongo import MongoClient
except ImportError:
    pass


# Code snipped taken from
# http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


class Mongodb (object):
    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.mongo_DB_store = None
        self.connection = None

    def preliminaries(self):
        if 'mongodb_plugin_server' not in self.agent_config or self.agent_config['mongodb_plugin_server'] == '':
            self.checks_logger.debug('mongodb_plugin: config not set')
            return False

        self.checks_logger.debug('mongodb_plugin: config set')

        try:
            import pymongo
            from pymongo import MongoClient

        except ImportError:
            self.checks_logger.error('mongodb_plugin: unable to import pymongo library')
            return False

        return True

    def get_connection(self):
        try:
            import urlparse
            parsed = urlparse.urlparse(self.agent_config['mongodb_plugin_server'])

            mongo_uri = ''

            # Can't use attributes on Python 2.4
            if parsed[0] != 'mongodb':

                mongo_uri = 'mongodb://'

                if parsed[2]:

                    if parsed[0]:

                        mongo_uri = mongo_uri + parsed[0] + ':' + parsed[2]

                    else:
                        mongo_uri = mongo_uri + parsed[2]

            else:

                mongo_uri = self.agent_config['mongodb_plugin_server']

            self.checks_logger.debug('-- mongo_uri: %s', mongo_uri)

            self.connection = MongoClient(mongo_uri, read_preference=pymongo.ReadPreference.SECONDARY)

            self.checks_logger.debug('Connected to MongoDB')

        except Exception:
            self.checks_logger.error(
                'Unable to connect to MongoDB server %s - Exception = %s', mongo_uri, traceback.format_exc())
            return False
        return True

    def run(self):
        self.checks_logger.debug('mongodb_plugin: started gathering data')

        if not self.preliminaries():
            return False

        if not self.get_connection():
            return False

        # Older versions of pymongo did not support the command()
        # method below.
        try:
            db = self.connection['local']

            # Server status
            status_output = db.command('serverStatus', recordStats=0)       # Shorthand for {'serverStatus': 1}

            self.checks_logger.debug('mongodb_plugin: executed serverStatus')

            # Setup
            status = {}

            # Version
            try:
                status['version'] = status_output['version']

                self.checks_logger.debug('mongodb_plugin: version %s', status_output['version'])

            except KeyError, ex:
                self.checks_logger.error('mongodb_plugin: version KeyError exception = %s', ex)
                pass

            # Global locks
            try:
                split_version = status['version'].split('.')
                split_version = map(lambda x: int(x), split_version)

                if (split_version[0] <= 2) and (split_version[1] < 2):

                    self.checks_logger.debug('mongodb_plugin: globalLock')

                    status['globalLock_ratio'] = status_output['globalLock']['ratio']
                    status['globalLock_currentQueue_total'] = status_output['globalLock']['currentQueue']['total']
                    status['globalLock_currentQueue_readers'] = status_output['globalLock']['currentQueue']['readers']
                    status['globalLock_currentQueue_writers'] = status_output['globalLock']['currentQueue']['writers']

                else:
                    self.checks_logger.debug('mongodb_plugin: version >= 2.2, not getting globalLock status')

            except KeyError, ex:
                self.checks_logger.error('mongodb_plugin: globalLock KeyError exception = %s', ex)
                pass

            # Memory
            try:
                self.checks_logger.debug('mongodb_plugin: memory')

                status['mem_resident'] = status_output['mem']['resident']
                status['mem_virtual'] = status_output['mem']['virtual']
                status['mem_mapped'] = status_output['mem']['mapped']

            except KeyError, ex:
                self.checks_logger.error('mongodb_plugin: memory KeyError exception = %s', ex)
                pass

            # Connections
            try:
                self.checks_logger.debug('mongodb_plugin: connections')

                status['connections_current'] = status_output['connections']['current']
                status['connections_available'] = status_output['connections']['available']

            except KeyError, ex:
                self.checks_logger.error('mongodb_plugin: connections KeyError exception = %s', ex)
                pass

            # Extra info (Linux only)
            try:
                self.checks_logger.debug('mongodb_plugin: extra info')

                status['extraInfo_heapUsage'] = status_output['extra_info']['heap_usage_bytes']
                status['extraInfo_pageFaults'] = status_output['extra_info']['page_faults']

            except KeyError, ex:
                self.checks_logger.debug('mongodb_plugin: extra info KeyError exception = %s', ex)
                pass

            # Background flushing
            try:
                self.checks_logger.debug('mongodb_plugin: backgroundFlushing')

                delta = datetime.datetime.utcnow() - status_output['backgroundFlushing']['last_finished']
                status['backgroundFlushing_secondsSinceLastFlush'] = delta.seconds
                status['backgroundFlushing_lastFlushLength'] = status_output['backgroundFlushing']['last_ms']
                status['backgroundFlushing_flushLengthAvrg'] = status_output['backgroundFlushing']['average_ms']

            except KeyError, ex:
                self.checks_logger.debug('mongodb_plugin: backgroundFlushing KeyError exception = %s', ex)
                pass

            # Per second metric calculations (opcounts and asserts)
            try:
                if self.mongo_DB_store is None:
                    self.checks_logger.debug('mongodb_plugin: per second metrics no cached data, so storing for first time')
                    self.set_mongo_db_store(status_output)

                else:
                    self.checks_logger.debug('mongodb_plugin: per second metrics cached data exists')

                    if (split_version[0] <= 2) and (split_version[1] < 4):

                        accesses_ps = float(status_output['indexCounters']['btree']['accesses'] - self.mongo_DB_store['indexCounters']['accessesPS']) / 60

                        if accesses_ps >= 0:
                            status['indexCounters_accessesPS'] = accesses_ps
                            status['indexCounters_hitsPS'] = float(status_output['indexCounters']['btree']['hits'] - self.mongo_DB_store['indexCounters']['hitsPS']) / 60
                            status['indexCounters_missesPS'] = float(status_output['indexCounters']['btree']['misses'] - self.mongo_DB_store['indexCounters']['missesPS']) / 60
                            status['indexCounters_missRatioPS'] = float(status_output['indexCounters']['btree']['missRatio'] - self.mongo_DB_store['indexCounters']['missRatioPS']) / 60

                    elif (split_version[0] <= 2) and (split_version[1] >= 4):

                        accesses_ps = float(status_output['indexCounters']['accesses'] - self.mongo_DB_store['indexCounters']['accessesPS']) / 60

                        if accesses_ps >= 0:
                            status['indexCounters_accessesPS'] = accesses_ps
                            status['indexCounters_hitsPS'] = float(status_output['indexCounters']['hits'] - self.mongo_DB_store['indexCounters']['hitsPS']) / 60
                            status['indexCounters_missesPS'] = float(status_output['indexCounters']['misses'] - self.mongo_DB_store['indexCounters']['missesPS']) / 60
                            status['indexCounters_missRatioPS'] = float(status_output['indexCounters']['missRatio'] - self.mongo_DB_store['indexCounters']['missRatioPS']) / 60
                    else:
                        self.checks_logger.debug('mongodb_plugin: per second metrics negative value calculated, mongod likely restarted, so clearing cache')

                    if accesses_ps >= 0:
                        status['opCounters_insertPS'] = float(status_output['opcounters']['insert'] - self.mongo_DB_store['opCounters']['insertPS']) / 60
                        status['opCounters_queryPS'] = float(status_output['opcounters']['query'] - self.mongo_DB_store['opCounters']['queryPS']) / 60
                        status['opCounters_updatePS'] = float(status_output['opcounters']['update'] - self.mongo_DB_store['opCounters']['updatePS']) / 60
                        status['opCounters_deletePS'] = float(status_output['opcounters']['delete'] - self.mongo_DB_store['opCounters']['deletePS']) / 60
                        status['opCounters_getmorePS'] = float(status_output['opcounters']['getmore'] - self.mongo_DB_store['opCounters']['getmorePS']) / 60
                        status['opCounters_commandPS'] = float(status_output['opcounters']['command'] - self.mongo_DB_store['opCounters']['commandPS']) / 60

                        status['asserts_regularPS'] = float(status_output['asserts']['regular'] - self.mongo_DB_store['asserts']['regularPS']) / 60
                        status['asserts_warningPS'] = float(status_output['asserts']['warning'] - self.mongo_DB_store['asserts']['warningPS']) / 60
                        status['asserts_msgPS'] = float(status_output['asserts']['msg'] - self.mongo_DB_store['asserts']['msgPS']) / 60
                        status['asserts_userPS'] = float(status_output['asserts']['user'] - self.mongo_DB_store['asserts']['userPS']) / 60
                        status['asserts_rolloversPS'] = float(status_output['asserts']['rollovers'] - self.mongo_DB_store['asserts']['rolloversPS']) / 60
                    if 'globalLock' in self.mongo_DB_store:
                        total_time = float(status_output['globalLock']['totalTime'] - self.mongo_DB_store['globalLock']['totalTime'])
                        lock_time = float(status_output['globalLock']['lockTime'] - self.mongo_DB_store['globalLock']['lockTime'])
                        status['global_lock_percent'] = (lock_time / total_time) * 100.0
                        highest_lock = 0
                        for database_name in status_output['locks'].keys():
                            if database_name in self.mongo_DB_store['locks'] and database_name in status_output['locks']:
                                if 'r' in status_output['locks'][database_name]['timeLockedMicros']:
                                    time_locked_r = float(status_output['locks'][database_name]['timeLockedMicros']['r'] - self.mongo_DB_store['locks'][database_name]['timeLockedMicros']['r'])
                                    time_locked_w = float(status_output['locks'][database_name]['timeLockedMicros']['w'] - self.mongo_DB_store['locks'][database_name]['timeLockedMicros']['w'])
                                elif 'R' in status_output['locks'][database_name]['timeLockedMicros']:
                                    time_locked_r = float(status_output['locks'][database_name]['timeLockedMicros']['R'] - self.mongo_DB_store['locks'][database_name]['timeLockedMicros']['R'])
                                    time_locked_w = float(status_output['locks'][database_name]['timeLockedMicros']['W'] - self.mongo_DB_store['locks'][database_name]['timeLockedMicros']['W'])
                                time_locked = time_locked_r + time_locked_w
                                if time_locked > highest_lock:
                                    highest_lock = time_locked
                        status['lock_percent'] = (lock_time + (highest_lock / 1000.0)) / float(total_time) * 100.0

            except KeyError, ex:
                self.checks_logger.error('mongodb_plugin: per second metrics KeyError exception = %s', ex)
                pass
            finally:
                try:
                    self.set_mongo_db_store(status_output)
                except:
                    self.checks_logger.error('mongodb_plugin: could not save metrics to calculate differentials')



            # Cursors
            try:
                self.checks_logger.debug('mongodb_plugin: cursors')

                status['cursors_totalOpen'] = status_output['cursors']['totalOpen']

            except KeyError, ex:
                self.checks_logger.error('mongodb_plugin: cursors KeyError exception = %s', ex)
                pass

            # Replica set status
            if 'MongoDBReplSet' in self.agent_config and self.agent_config['MongoDBReplSet'] == 'yes':
                self.checks_logger.debug('mongodb_plugin: get replset status too')

                # isMaster (to get state
                isMaster = db.command('isMaster')

                self.checks_logger.debug('mongodb_plugin: executed isMaster')

                status['replSet_setName'] = isMaster['setName']
                status['replSet_isMaster'] = isMaster['ismaster']
                status['replSet_isSecondary'] = isMaster['secondary']

                if 'arbiterOnly' in isMaster:
                    status['replSet_isArbiter'] = isMaster['arbiterOnly']

                self.checks_logger.debug('mongodb_plugin: finished isMaster')

                # rs.status()
                db = self.connection['admin']
                repl_set = db.command('replSetGetStatus')

                self.checks_logger.debug('mongodb_plugin: executed replSetGetStatus')

                status['replSet_myState'] = repl_set['myState']

                status['replSet_members'] = {}

                for member in repl_set['members']:

                    self.checks_logger.debug('mongodb_plugin: replSetGetStatus looping %s', member['name'])

                    status['replSet']['members'][str(member['_id'])] = {}

                    status['replSet']['members'][str(member['_id'])]['name'] = member['name']
                    status['replSet']['members'][str(member['_id'])]['state'] = member['state']

                    # Optime delta (only available from not self)
                    # Calculation is from http://docs.python.org/library/datetime.html#datetime.timedelta.total_seconds
                    if 'optimeDate' in member:          # Only available as of 1.7.2
                        deltaOptime = datetime.datetime.utcnow() - member['optimeDate']
                        status['replSet']['members'][str(member['_id'])]['optimeDate'] = (deltaOptime.microseconds + (deltaOptime.seconds + deltaOptime.days * 24 * 3600) * 10**6) / 10**6

                    if 'self' in member:
                        status['replSet']['myId'] = member['_id']

                    # Have to do it manually because total_seconds() is only available as of Python 2.7
                    else:
                        if 'lastHeartbeat' in member:
                            delta_heartbeat = datetime.datetime.utcnow() - member['lastHeartbeat']
                            status['replSet']['members'][str(member['_id'])]['lastHeartbeat'] = (delta_heartbeat.microseconds + (delta_heartbeat.seconds + delta_heartbeat.days * 24 * 3600) * 10**6) / 10**6

                    if 'errmsg' in member:
                        status['replSet']['members'][str(member['_id'])]['error'] = member['errmsg']

            # db.stats()
            if 'MongoDBDBStats' in self.agent_config and self.agent_config['MongoDBDBStats'] == 'yes':
                self.checks_logger.debug('mongodb_plugin: db.stats() too')

                for database in self.connection.database_names():

                    if database != 'config' and database != 'local' and database != 'admin' and database != 'test':

                        self.checks_logger.debug('mongodb_plugin: executing db.stats() for %s', database)

                        dbstats_database = 'dbStats_{0}'.format(database)
                        dbstats_database_namespaces = 'dbStats_{0}_namespaces'.format(database)

                        status[dbstats_database] = self.connection[database].command('dbstats')
                        status[dbstats_database_namespaces] = self.connection[database]['system']['namespaces'].count()

                        # Ensure all strings to prevent JSON parse errors. We typecast on the server
                        for key in status[dbstats_database].keys():

                            status[dbstats_database][key] = str(status[dbstats_database][key])

        except Exception:
            import traceback
            self.checks_logger.error('mongodb_plugin: unable to get MongoDB status - Exception = %s', traceback.format_exc())
            return False

        self.checks_logger.debug('mongodb_plugin: completed, returning')

        flatten_status = flatten(status)
        return flatten_status

    def set_mongo_db_store(self, status_output):

        split_version = status_output['version'].split('.')
        split_version = map(lambda x: int(x), split_version)
        self.mongo_DB_store = {
            'indexCounters': {},
            'opCounters': {},
            'asserts': {}
        }

        if (split_version[0] <= 2) and (split_version[1] < 4):

            self.mongo_DB_store['indexCounters']['accessesPS'] = status_output['indexCounters']['btree']['accesses']
            self.mongo_DB_store['indexCounters']['hitsPS'] = status_output['indexCounters']['btree']['hits']
            self.mongo_DB_store['indexCounters']['missesPS'] = status_output['indexCounters']['btree']['misses']
            self.mongo_DB_store['indexCounters']['missRatioPS'] = status_output['indexCounters']['btree']['missRatio']

        elif (split_version[0] <= 2) and (split_version[1] >= 4):

            self.mongo_DB_store['indexCounters']['accessesPS'] = status_output['indexCounters']['accesses']
            self.mongo_DB_store['indexCounters']['hitsPS'] = status_output['indexCounters']['hits']
            self.mongo_DB_store['indexCounters']['missesPS'] = status_output['indexCounters']['misses']
            self.mongo_DB_store['indexCounters']['missRatioPS'] = status_output['indexCounters']['missRatio']

        if 'globalLock' in status_output and 'totalTime' in status_output['globalLock'] and 'lockTime' in status_output['globalLock']:
            self.mongo_DB_store['globalLock'] = {}
            self.mongo_DB_store['globalLock']['totalTime'] = status_output['globalLock']['totalTime']
            self.mongo_DB_store['globalLock']['lockTime'] = status_output['globalLock']['lockTime']
            self.mongo_DB_store['locks'] = status_output['locks']

        self.mongo_DB_store['opCounters']['insertPS'] = status_output['opcounters']['insert']
        self.mongo_DB_store['opCounters']['queryPS'] = status_output['opcounters']['query']
        self.mongo_DB_store['opCounters']['updatePS'] = status_output['opcounters']['update']
        self.mongo_DB_store['opCounters']['deletePS'] = status_output['opcounters']['delete']
        self.mongo_DB_store['opCounters']['getmorePS'] = status_output['opcounters']['getmore']
        self.mongo_DB_store['opCounters']['commandPS'] = status_output['opcounters']['command']

        self.mongo_DB_store['asserts']['regularPS'] = status_output['asserts']['regular']
        self.mongo_DB_store['asserts']['warningPS'] = status_output['asserts']['warning']
        self.mongo_DB_store['asserts']['msgPS'] = status_output['asserts']['msg']
        self.mongo_DB_store['asserts']['userPS'] = status_output['asserts']['user']
        self.mongo_DB_store['asserts']['rolloversPS'] = status_output['asserts']['rollovers']

if __name__ == "__main__":
    """Standalone test
    """
    import logging
    import sys
    import json
    import time
    import time
    host = '127.0.0.1'
    port = '27017'

    main_agent_config = {
        'mongodb_plugin_server': "{0}:{1}".format(host, port),
        'mongodb_plugin_dbstats': 'yes'
    }

    main_checks_logger = logging.getLogger('MongodbPlugin')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    mongo_check = Mongodb(main_agent_config, main_checks_logger, {})
    while True:
        try:
            result = mongo_check.run()
            print json.dumps(result, indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)