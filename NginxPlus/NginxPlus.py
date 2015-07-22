#
# Server Density Plugin
# nginx Plus
#
# https://www.serverdensity.com/plugins/nginx/
# https://github.com/serverdensity/sd-agent-plugins/

#
# Version: 1.0.0
#

import httplib
import json
import urllib2


class NginxPlus (object):
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
        if self.agentConfig.get('nginx_status_url') != '':
            self.checksLogger.debug('NginxPlus: starting')

            status = self.getStatus()

            if status:

                data = {}

                # Connections
                if 'connections' in status:
                    data['connections_accepted'] = status['connections'].get(
                        'accepted', None)
                    data['connections_dropped'] = status['connections'].get(
                        'dropped', None)
                    data['connections_active'] = status['connections'].get(
                        'active', None)
                    data['connections_idle'] = status['connections'].get(
                        'idle', None)

                # Requests
                data['requests_total'] = status['requests']['total']
                data['requests_current'] = status['requests']['current']

                # Server zones
                if 'server_zones' in status:
                    for zone, items in status['server_zones'].iteritems():
                        # Requests
                        name = 'zone_%s_requests' % zone
                        data[name] = items.get('requests', None)

                        if 'responses' in items:
                            # Responses
                            name = 'zone_%s_responses' % zone
                            data[name] = items['responses'].get('total', None)

                            # Responses: 1xx
                            name = 'zone_%s_responses_1xx' % zone
                            data[name] = items['responses'].get('1xx', None)

                            # Responses: 2xx
                            name = 'zone_%s_responses_2xx' % zone
                            data[name] = items['responses'].get('2xx', None)

                            # Responses: 3xx
                            name = 'zone_%s_responses_3xx' % zone
                            data[name] = items['responses'].get('3xx', None)

                            # Responses: 4xx
                            name = 'zone_%s_responses_4xx' % zone
                            data[name] = items['responses'].get('4xx', None)

                            # Responses: 5xx
                            name = 'zone_%s_responses_5xx' % zone
                            data[name] = items['responses'].get('5xx', None)

                # Upstreams
                if 'upstreams' in status:
                    for group, servers in status['upstreams'].iteritems():

                        for server in servers:

                            if 'server' in server:
                                # State
                                name = 'upstream_%s_%s_state' % (
                                    group, server['server'])
                                data[name] = server.get('state', 'unknown')

                                # Requests
                                name = 'upstream_%s_%s_requests' % (
                                    group, server['server'])
                                data[name] = server.get('requests', None)

                                # Responses
                                if 'responses' in server:
                                    name = 'upstream_%s_%s_responses_total' % (
                                        group, server['server'])
                                    data[name] = server['responses'].get(
                                        'total', None)

                                    # Requests: 1xx
                                    name = 'upstream_%s_%s_responses_1xx' % (
                                        group, server['server'])
                                    data[name] = server['responses'].get(
                                        '1xx', None)

                                    # Responses: 2xx
                                    name = 'upstream_%s_%s_responses_2xx' % (
                                        group, server['server'])
                                    data[name] = server['responses'].get(
                                        '2xx', None)

                                    # Responses: 3xx
                                    name = 'upstream_%s_%s_responses_3xx' % (
                                        group, server['server'])
                                    data[name] = server['responses'].get(
                                        '3xx', None)

                                    # Responses: 4xx
                                    name = 'upstream_%s_%s_responses_4xx' % (
                                        group, server['server'])
                                    data[name] = server['responses'].get(
                                        '4xx', None)

                                    # Responses: 5xx
                                    name = 'upstream_%s_%s_responses_5xx' % (
                                        group, server['server'])
                                    data[name] = server['responses'].get(
                                        '5xx', None)

                                # Fails
                                name = 'upstream_%s_%s_fails' % (
                                    group, server['server'])
                                data[name] = server.get('fails', None)

                                # Unavail
                                name = 'upstream_%s_%s_unavail' % (
                                    group, server['server'])
                                data[name] = server.get('unavail', None)

                return data

            else:
                return False

        else:
            self.checksLogger.debug('NginxPlus: Nginx status URL not set')
            return False

    def getStatus(self):
        try:
            self.checksLogger.debug('NginxPlus: attempting urlopen')

            req = urllib2.Request(
                self.agentConfig['nginx_status_url'], None, headers)

            # Do the request, log any errors
            request = urllib2.urlopen(req)
            response = request.read()

        except urllib2.HTTPError, e:
            self.checksLogger.error(
                'NginxPlus: Unable to get Nginx status - HTTPError = %s', e)
            return False

        except urllib2.URLError, e:
            self.checksLogger.error(
                'NginxPlus: Unable to get Nginx status - URLError = %s', e)
            return False

        except httplib.HTTPException, e:
            self.checksLogger.error(
                'NginxPlus: Unable to get Nginx status - HTTPException = %s',
                e)
            return False

        except Exception:
            import traceback
            self.checksLogger.error(
                'NginxPlus: Unable to get Nginx status - Exception = %s',
                traceback.format_exc())
            return False

        self.checksLogger.debug('NginxPlus: urlopen success')

        try:
            status = json.loads(response)

        except Exception:
            import traceback
            self.checksLogger.error(
                'NginxPlus: JSON parsing error - Exception = %s',
                traceback.format_exc())
            return False

        self.checksLogger.debug('NginxPlus: parsed JSON')

        return status
