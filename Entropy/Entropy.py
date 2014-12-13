"""
  Server Density Plugin
  Available Entropy on system
  http://plugins.serverdensity.com/entropy/
  https://github.com/serverdensity/sd-agent-plugins/
  Autor: @bitbeans
  Version: 1.0.0
"""

import subprocess
from decimal import *

class Entropy (object):
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
        e = subprocess.check_output("cat /proc/sys/kernel/random/entropy_avail", shell=True)
        data = {'available': float(e)}
        return data
