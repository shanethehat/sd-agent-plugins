"""
  Server Density Plugin
  HA Proxy
  https://github.com/serverdensity/sd-agent-plugins/

  Version 1.0.0
"""

import csv
import os
from urllib import urlopen


class HAProxyPro:

    def __init__(self, agentConfig, logger, rawConfig):
        logger.debug("HAProxy - initializing")
        self.agent_config = agentConfig
        self.logger = logger
        self.raw_config = rawConfig

        logger.debug("HAProxy - initialized")

    def num(self, s):
        if s:
            return int(s)
        else:
            return 0

    def main(self):
        self.logger.debug("HAProxy - inside main()")

        if 'haproxy_url' not in self.raw_config['HAProxyPro']:
            self.logger.error(
                "HAProxy - haproxy_url required in /etc/sd-agent/config.cfg "
                "but missing")
            return False

        self.status_page_url = (self.raw_config['HAProxyPro']['haproxy_url'] +
                                "/;csv;norefresh")
        self.getStatusPage()
        self.logger.debug("HAProxy - status page")
        self.parseStatusPage()
        self.createKeyedStatus()
        return self.parseTotals()

    def getStatusPage(self):
        response = urlopen(self.status_page_url).read()
        self.raw_status = response  # [2:]

    def parseStatusPage(self):
        self.parsed_status = []

        reader = csv.DictReader(self.raw_status.split('\n'), delimiter=',')
        for row in reader:
            self.parsed_status.append(row)

    def createKeyedStatus(self):
        self.servers = {}

        for server in self.parsed_status:
            self.logger.debug("HAProxy - Server found: " + server['svname'])

            self.servers[server['# pxname'] + "_" + server['svname']] = {
                'sessions-per-second': self.num(server['rate']),
                'sessions-current': self.num(server['scur']),
                'sessions-max': self.num(server['smax']),
                'sessions-limit': self.num(server['slim']),
                'sessions-total': self.num(server['stot']),
                'sessions-rate-limit': self.num(server['rate_lim']),
                'sessions-rate-max': self.num(server['rate_max']),
                'bytes-in': self.num(server['bin']),
                'bytes-out': self.num(server['bout']),
                'server-active': self.num(server['act']),
                'server-backup': self.num(server['bck']),
                'connection-errors': self.num(server['econ']),
                'failed-health-checks': self.num(server['hanafail']),
                'response-errors': self.num(server['eresp']),
                'responses-denied': self.num(server['dresp']),
                'responses-1xx': self.num(server['hrsp_1xx']),
                'responses-2xx': self.num(server['hrsp_2xx']),
                'responses-3xx': self.num(server['hrsp_3xx']),
                'responses-4xx': self.num(server['hrsp_4xx']),
                'responses-5xx': self.num(server['hrsp_5xx']),
                'responses-xxx': self.num(server['hrsp_other']),
                'client-aborts': self.num(server['cli_abrt']),
                'server-aborts': self.num(server['srv_abrt']),
                'lb-total': self.num(server['lbtot']),
                'request-errors': self.num(server['ereq']),
                'requests-denied': self.num(server['dreq']),
                'requests-per-second': self.num(server['req_rate']),
                'requests-per-second-max': self.num(server['req_rate_max']),
                'requests-total': self.num(server['req_tot']),
                'requests-queued-current': self.num(server['qcur']),
                'requests-queued-max': self.num(server['qmax']),
                'server-type': self.num(server['type']),
                'server-weight': self.num(server['weight']),
                'retries': self.num(server['wretr']),
                'redispatches': self.num(server['wredis']),
            }

        self.logger.debug(self.servers.keys())

    def parseTotals(self):
        totals = {}

        for server_name, stats in self.servers.items():
            self.logger.debug("HAProxy - Parsing server stats: " + server_name)
            for key, val in stats.items():
                if totals.get(key):
                    totals[key] += val
                else:
                    totals[key] = val

        self.logger.debug("HAProxy - stats totals")
        self.logger.debug(totals)
        return totals

    def clean_url(self):
        return

    def run(self):
        self.logger.debug("HAProxy - run()")
        self.logger.debug(
            "Running in directory: " + os.getcwd() +
            " in path " + os.path.realpath(__file__))

        try:
            self.logger.debug("HAProxy - running main()")
            return self.main()
        except Exception, e:
            import traceback
            self.logger.error('HAProxy - failure \n' + traceback.format_exc())
0
