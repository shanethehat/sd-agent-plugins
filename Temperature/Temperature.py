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
    """SD Plugin for reading available temperature data from the machine.

    We need tools to be installed to complete fetching the temperatues:

    * lm-sensors - http://www.lm-sensors.org/
    * smartctl - http://www.smartmontools.org/

    Ubuntu Packages:
    * lm-sensors - http://packages.ubuntu.com/trusty/lm-sensors
    * smartctl - http://packages.ubuntu.com/trusty/smartmontools

    """

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()

        # Celsius our default
        self.temperature_scale = self.raw_config['Temperature']\
            .get('scale', 'c')

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
        """Extract from the onboard temperature sensor for a Pi
        """
        data = {}

        temp_sensor = '/sys/class/thermal/thermal_zone0/temp'

        try:
            with open(temp_sensor, 'r') as temp_device:
                temp = temp_device.read()
            temp_device.close()
        except Exception as exception:
            self.checks_logger.error(
                'Failed to open file to read temperature: {0}'.format(
                    exception.message))

        try:
            # / 1000 as the value returned is very precise
            data['Core 0'] = self.convert_reading(float(int(temp) / 1000.0))
        except Exception as exception:
            self.checks_logger.error(
                'Failed to calculate temperature: {0}'.format(
                    exception.message))
        return data

    def process_linux(self):
        """Do the right thing for a linux server.
        """
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
                            = reading.replace('C', '')

            if 'disks' in self.raw_config['Temperature']:
                data = self.read_disk_temperatures(data)

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
        """Convert Celsius to Kelvin, because why not?"""
        return float(temperature_in_celsius) + 273.15

    def convert_celsius_to_fahrenheit(self, temperature_in_celsius):
        """Convert Celsius to Fahrenheit"""
        return float(temperature_in_celsius * 9) / 5 + 32

    def read_disk_temperatures(self, data):
        """ Use smartctl to read the temperature from the available disks.
        """
        # check if we can read the disks
        # also check if the config knows which disks or just all of them
        if 'disks' in self.raw_config['Temperature'] and\
           self.raw_config['Temperature']['disks'] != 'yes':
            disks = self.raw_config['Temperature']['disks'].split(',')
        else:
            try:
                import glob
                disks = glob.glob('/dev/sd[a-z]')
            except ImportError as exception:
                self.checks_logger.error(
                    'Unable to import "glob" Python module')
                return data

        for disk in disks:
            proc = subprocess.Popen(['sudo',
                                     'smartctl',
                                     '--all',
                                     disk,
                                     '-s',
                                     'on'],
                                    stdout=subprocess.PIPE, close_fds=True)
            output = proc.communicate()[0]
            for line in output.split("\n"):
                split = line.split()
                try:
                    if 'Temperature_Celsius' in split:
                        if self.temperature_scale == 'f':
                            data[disk] =\
                                self.convert_celsius_to_fahrenheit(split[9])
                        elif self.temperature_scale == 'k':
                            data[disk] =\
                                self.convert_celsius_to_kelvin(split[9])
                        else:
                            data[disk] = split[9]
                except Exception as exception:
                    self.checks_logger.error(
                        'Unable to extract temperature from smartctl.'
                        'Error: {0}'.format(exception.message))
        return data


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Temperature': {
            'scale': 'c',
            'cpus': 'yes',
            'other': 'yes',
            'adapters': 'f75375-i2c-0-2d',
            'disks': 'yes'  # 'disks': '/dev/sdc,/dev/sdd'
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
