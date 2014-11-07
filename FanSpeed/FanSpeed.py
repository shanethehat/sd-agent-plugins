"""
  Server Density Plugin
  Fan Speed measurements

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


class FanSpeed(object):
    """SD Plugin for reading available fan speedsfrom the machine.

    We need tools to be installed to complete fetching the temperatues:

    * lm-sensors - http://www.lm-sensors.org/

    Ubuntu Packages:
    * lm-sensors - http://packages.ubuntu.com/trusty/lm-sensors

    """

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()


    def run(self):

        data = {}

        if 'FanSpeed' not in self.raw_config:
            return False

        if platform.system() == 'Linux':
            data = self.process()

        return data

    def process(self):
        """Do the right thing for a linux server.
        """
        data = {}

        proc = subprocess.Popen(
            ['sensors'],
            stdout=subprocess.PIPE,
            close_fds=True)

        fans = proc.communicate()[0]

        for sensors_output_line in fans.split("\n"):

            fan = None

            if not sensors_output_line\
               and not sensors_output_line.startswith('fan'):
                continue

            if sensors_output_line.startswith('fan'):

                try:
                    speed = sensors_output_line.split(':')[1].split('RPM')[0].strip()
                except Exception as exception:
                    self.mainLogger.error(
                        'Failed to find RPM speed: Error {0}'.format(exception.message)
                    continue

                try:
                    fan = sensors_output_line.split(':')[0]
                except Exception as exception:
                    self.mainLogger.error(
                        'Failed to find RPM speed: Error {0}'.format(exception.message)
                    continue


                if fan\
                   and fan not in self.raw_config['FanSpeed'].get('ignore', []):
                    data[fan] = speed

        return data


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'FanSpeed': {
            'ignore': 'fan2' # or 'none'
        }
    }

    main_checks_logger = logging.getLogger('FanSpeed')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    fan_speed_check = FanSpeed({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(fan_speed_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)