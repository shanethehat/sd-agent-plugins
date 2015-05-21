import subprocess

nagiosPluginsCommandLines = [
    "/usr/lib64/nagios/plugins/check_sensors",
    "/usr/lib64/nagios/plugins/check_mailq -w 10 -c 20 -M postfix",
]


class NagiosWrapper:
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
        data = {}
        for pluginCommandLine in nagiosPluginsCommandLines:

            # subprocess needs a list containing the command and
            # its parameters
            pluginCommandLineList = pluginCommandLine.split(" ")
            # the check command to retrieve it's name
            pluginCommand = pluginCommandLineList[0]

            p = subprocess.Popen(
                pluginCommandLineList,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = p.communicate()

            self.checksLogger.debug(
                'Output of {0}: {1}'.format(pluginCommand, out)
            )

            if err:
                self.checksLogger.error(
                    'Error executing {0}: {1}'.format(pluginCommand, err)
                )

            # the check command name = return value:
            # 0 - OK
            # 1 - WARNING
            # 2 - CRITICAL
            # 3 - UNKNOWN
            data[pluginCommand.split("/")[-1]] = p.returncode

            # add performance data if it exists
            perfData = out.split("|")
            if len(perfData) > 1:
                data[perfData[1].split(";")[0].split("=")[0]] = perfData[
                    1].split(";")[0].split("=")[1]

        return data
