"""
  Server Density Plugin
  Power measurements

  https://www.serverdensity.com/plugins/power/
  https://github.com/serverdensity/sd-agent-plugins/


  Version: 1.0.0
"""

import json
import logging
import platform
import sys
import subprocess
import time


class Power(object):
    """SD Plugin for reading available power data from the machine.

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

        if platform.system() == 'Linux':
            return self.process_linux()
        return {}

    def process_linux(self):
        data = {}
        proc = subprocess.Popen(['sensors', '-A'], stdout=subprocess.PIPE, close_fds=True)
        temps = proc.communicate()[0]

        for temp_line in temps.split("\n"):

            if not temp_line:
                continue

            # we are starting a new adapter/thing
            if not ':' in temp_line:
                adapter_name = temp_line

            # allow bypass of bad data
            if adapter_name not in self.raw_config['Power']['adapters'].split(','):
                continue

            if temp_line.startswith('power'):
                line = temp_line.split()
                watts = line[1]
                data[line[0].replace(':', '') + ' ' + adapter_name] = watts

        return data


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Power': {
            'adapters': 'fam15h_power-pci-00c4,fam15h_power-pci-00cc',
        }
    }

    main_checks_logger = logging.getLogger('Power')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    power_check = Power({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(power_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
