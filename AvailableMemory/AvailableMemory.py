import subprocess
import re


class AvailableMemory:
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
        data = {}

        p = subprocess.Popen(
            ['free', '-m'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        freeOutput, errorOutput = p.communicate()

        self.checksLogger.debug(
            'Free memory command output: {0}'.format(freeOutput)
        )

        if errorOutput:
            self.checksLogger.error(
                'Error executing memory information: {0}'.format(errorOutput))

        old_ver = re.search('cache:\s+\d+\s+(?P<available>\d+)', freeOutput)
        new_ver = re.search('Mem:(\s+\d+){5}\s+(?P<available>\d+)', freeOutput)

        if old_ver:
            data['Available memory'] = old_ver.group('available')
        elif new_ver:
            data['Available memory'] = new_ver.group('available')
        else:
            self.checksLogger.debug(
                'Something went wrong, and the plugin returned no data')

        return data
