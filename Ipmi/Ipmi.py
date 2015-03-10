"""
  Server Density Plugin
  IPMI measurements (temp, fan, power)

  https://github.com/serverdensity/sd-agent-plugins/


  Version: 1.0.0
"""

import re
import json
import logging
import sys
import subprocess
import time


class Ipmi(object):
    """SD Plugin for reading available data from the machines IPMI board sensors.

    We need tools to be installed to query the IPMI interface:

    * ipmitool - http://ipmitool.sourceforge.net/
    """

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config

    def run(self):

        data = {}

        if 'Ipmi' not in self.raw_config:
            return False

        proc = subprocess.Popen(
            ['sudo','ipmitool', 'sensor'],
            stdout=subprocess.PIPE,
            close_fds=True)

        self.sensors = proc.communicate()[0]

        if self.raw_config['Ipmi']['cpus'] == 'yes':
            data.update(self.process_cpus())

        if self.raw_config['Ipmi']['system'] == 'yes':
            data.update(self.process_system())

        if self.raw_config['Ipmi']['peripheral'] == 'yes':
            data.update(self.process_peripheral())

        if self.raw_config['Ipmi']['fans'] == 'yes':
            data.update(self.process_fans())

        if self.raw_config['Ipmi']['powersupply'] == 'yes':
            data.update(self.process_powersupply())

        return data

    def process_cpus(self):
        """Collect temperatures from all available CPUs"""
        data = {}

        cpu_matcher = re.compile(r'^CPU(\d*)\sTemp').match

        for sensor in self.sensors.split("\n"):
            match = cpu_matcher(sensor)
            if match:
                if match.group(1):
                    cpu_num = match.group(1)
                else:
                    cpu_num = 1

                data['temp-cpu-{0}'.format(cpu_num)] = float(sensor.split('|')[1].strip())

        return data

    def process_system(self):
        """Collect system temperature"""
        data = {}

        for sensor in self.sensors.split("\n"):
            if sensor.startswith('System Temp'):
                data['temp-system'] = float(sensor.split('|')[1].strip())

        return data

    def process_peripheral(self):
        """Collect peripheral temperature"""
        data = {}

        for sensor in self.sensors.split("\n"):
            if sensor.startswith('Peripheral Temp'):
                data['temp-peripheral'] = float(sensor.split('|')[1].strip())

        return data


    def process_fans(self):
        """Collect speed from all available Fans"""
        data = {}

        fan_matcher = re.compile(r'^FAN(\w+)').match

        for sensor in self.sensors.split("\n"):
            match = fan_matcher(sensor)
            if match:
                columns = sensor.split('|')
                if columns[1].strip() != 'na':
                    data['speed-fan-{0}'.format(match.group(1))] = float(columns[1].strip())

        return data

    def process_powersupply(self):
        """Collect power supply status"""
        data = {}

        ps_matcher = re.compile(r'^PS(\d+) Status').match

        for sensor in self.sensors.split("\n"):
            match = ps_matcher(sensor)
            if match:
                columns = sensor.split('|')
                if columns[1].strip() != 'na':
                    data['power-supply-{0}'.format(match.group(1))] = int(columns[1].strip(), 16)

        return data

if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Ipmi': {
            'cpus': 'yes',
            'system': 'yes',
            'peripheral': 'yes',
            'fans': 'yes',
            'powersupply': 'yes',
        }
    }

    main_checks_logger = logging.getLogger('Ipmi')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    ipmi_check = Ipmi({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(ipmi_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(5)
