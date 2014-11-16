"""
  Server Density Plugin
  Temperature measurements

  https://www.serverdensity.com/plugins/temperatures/
  https://github.com/serverdensity/sd-agent-plugins/


  Version: 1.0.0
"""

import json
import logging
import os
import platform
import sys
import subprocess
import time


class Docker(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()
        self.docker_path = [
            '/sys/fs/cgroup/memory/docker',
            '/sys/fs/cgroup/cpu/docker',
        ]

    def run(self):

        data = {}

        container_id = None
        
        names = self.extract_container_names()
        print names

        for container_id, container_name in names.iteritems():
            for path in self.docker_path:
                for dir_name in os.listdir(path):
                    try:
                        container_dir = os.path.join(path, dir_name)
                        if not os.path.isdir(container_dir):
                            continue
                        for file_name in os.listdir(container_dir):
                            try:
                                with open(os.path.join(container_dir, file_name), 'r') as temp_file:
                                    reading = temp_file.read()
                                temp_file.close()
                                reading = reading.split('\n')
                                # deal multiple values in a file
                                if len(reading) > 3:
                                    for read in reading:
                                        if read:
                                            split_reading = read.split()
                                            print split_reading
                                            if '=' in split_reading[0]:
                                                name, reading = split_reading[0].split('=')
                                            else:
                                                name, reading = split_reading[0], split_reading[1]
                                            data[container_name + '-' + name] = reading
                                else:
                                    print os.path.join(container_dir, file_name)
                                    data[container_name + '-' + file_name] = reading[0]
                            except Exception as exception:
                                print exception
                        
                    except Exception as exception:
                        self.mainLogger.error(
                            'Failed to open file to read temperature: {0}'.format(
                            exception.message))

        return data

    def extract_container_names(self):
        """ Iterate over the output of:
            sudo docker ps -l
            CONTAINER ID IMAGE        COMMAND   CREATED      STATUS      PORTS NAMES
            491f2fe3b18f ubuntu:14.04 /bin/bash 40 hours ago Up 40 hours       focused_feynman
        """

        names = {}

        proc = subprocess.Popen(
                    ['sudo', 'docker', 'ps', '-l'],
                    stdout=subprocess.PIPE,
                    close_fds=True)
        docker_ps = proc.communicate()[0]

        for line in docker_ps.split('\n'):
            if not line or line.startswith('CONTAINER ID'):
                continue
            line = line.split()
            names[line[0]] = line[-1]

        return names
                       


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Docker': {
            'container_name': 'focused_feynman',
        }
    }

    main_checks_logger = logging.getLogger('Docker')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    docker_check = Docker({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(docker_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
