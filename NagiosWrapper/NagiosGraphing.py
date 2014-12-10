import subprocess

nagiosPluginsCommandLines = [
    "/usr/local/nagios/libexec/check_eximqueue -w 250 -c 500",
]


class NagiosGraphing:
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

            p = subprocess.Popen(pluginCommandLineList, stdout=subprocess.PIPE)
            out, err = p.communicate()

            for line in out.split('\n'):
                if 'check_eximqueue' in pluginCommandLine:
                    data['check_eximqueue'] = out.split()[3]

        return data
