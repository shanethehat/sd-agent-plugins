"""
  Server Density Plugin
  Temperature measurements

  https://www.serverdensity.com/plugins/temperatures/
  https://github.com/serverdensity/sd-agent-plugins/


  Version: 1.0.0
"""

import json
import logging
import platform
import sys
import subprocess
import time


class Temperature(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()

        self.temperature_scale = self.raw_config['Temperature']['scale']

    def run(self):

        data = {}

        if 'Temperature' not in self.raw_config:
            return False

        if platform.machine() == 'armv6l':
            data = self.process_linux_pi()
        elif platform.system() == 'Linux':
            data = self.process_linux()

        return data

    def process_linux_pi(self):
        data = {}

        temp_sensor = '/sys/class/thermal/thermal_zone0/temp'

        try:
            with open(temp_sensor, 'r') as temp_device:
                temp = temp_device.read()
            temp_device.close()
        except Exception as exception:
            self.mainLogger.error(
                'Failed to open file to read temperature: {0}'.format(
                    exception.message))

        try:
            data['Core 0'] = self.convert_reading(float(int(temp) / 1000.0))
        except Exception as exception:
            self.mainLogger.error(
                'Failed to calculate temperature: {0}'.format(
                    exception.message))
        return data

    def process_linux(self):
        data = {}

        for adapter in self.raw_config['Temperature']['adapters'].split(','):
            if self.temperature_scale == 'f':
                proc = subprocess.Popen(
                    ['sensors', '{0}', '-{1}'.format(adapter,
                                                     self.temperature_scale)],
                    stdout=subprocess.PIPE,
                    close_fds=True)
            else:
                proc = subprocess.Popen(
                    ['sensors', '{0}'.format(adapter)],
                    stdout=subprocess.PIPE,
                    close_fds=True)

            temps = proc.communicate()[0]
            temps = temps.replace("\xc2\xb0C", '')

            for temp_line in temps.split("\n"):

                if not temp_line:
                    continue

                if self.raw_config['Temperature']['cpus'] == 'yes':
                    if temp_line.startswith('Core'):
                        reading = temp_line.replace(' ', '').split('+')[1]\
                            .split('(')[0]
                        data['{0} {1}'.format(adapter,
                                              temp_line.split(':')[0])]\
                            = reading

                if self.raw_config['Temperature']['other'] == 'yes':
                    if 'hyst' in temp_line:
                        reading = temp_line.replace(' ', '').split('+')[1]\
                            .split('(')[0]
                        data['{0} {1}'.format(adapter,
                                              temp_line.split(':')[0])]\
                            = reading

        return data

    def convert_reading(self, temperature):
        """We read everything in Celsius
        we can convert it to either Kelvin or Fahrenheit"""

        if self.temperature_scale == 'f':
            return self.convert_celsius_to_fahrenheit(temperature)
        elif self.temperature_scale == 'k':
            return self.convert_celsius_to_kelvin(temperature)
        else:
            return temperature

    def convert_celsius_to_kelvin(self, temperature_in_celsius):
        return float(temperature_in_celsius) + 273.15

    def convert_celsius_to_fahrenheit(self, temperature_in_celsius):
        return float(temperature_in_celsius * 9) / 5 + 32


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Temperature': {
            'scale': 'c',
            'cpus': 'yes',
            'other': 'yes',
            'adapters': 'f75375-i2c-0-2d,f75375-i2c-0-2f'
        }
    }

    main_checks_logger = logging.getLogger('Temperature')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    temperature_check = Temperature({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(temperature_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
