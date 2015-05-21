import subprocess
import re


class FreeMemory:
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

        matches = re.search('cache:\s+\d+\s+(?P<total_free>\d+)', freeOutput)

        if matches:
            data['Free memory'] = matches.group('total_free')

        return data
