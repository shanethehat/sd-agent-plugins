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

        matches = re.search('cache:\s+\d+\s+(?P<available>\d+)', freeOutput)

        if matches:
            data['Available memory'] = matches.group('available')

        return data
