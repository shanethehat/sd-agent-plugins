# nagios-wrapper

## Server Density plugin to wrap Nagios plugins

Deploy the plugin (NagiosWrapper.py file) to Server Density Agent plugin directory, as described on:
http://support.serverdensity.com/knowledgebase/articles/76018-writing-a-plugin-linux-mac-and-freebsd

Use the first lines as examples for your own Nagios plugins:

`` `nagiosPluginsCommandLines = [
         "/usr/lib64/nagios/plugins/check_sensors",
         "/usr/bin/sd-agent/check_mailq -w 10 -c 20 -M postfix",
         ]` ``

these can be changed to contain the Nagios plugins command lines that will be used.

Two important aspects are relevant to making sure the Nagios plugins runs as expected:

1. The command line is correct. The best way to test it is to run it as sd-agent user:
`` `$ sudo -u sd-agent /usr/lib64/nagios/plugins/check_sensors
sensor ok` ``
2. Some plugins may need root permissions to run. In this case a sudo wrapper may need to be deployed:
* add a sudoers permission, using visudo append: 
`` `sd-agent ALL=NOPASSWD:/usr/lib64/nagios/plugins/check_mailq` ``
* create a wrapper for the actual plugin command: 
`` `$ cat /usr/bin/sd-agent/check_mailq
#!/bin/bash
sudo /usr/lib64/nagios/plugins/check_mailq $@` ``

After deployment, all that is necessary is a restart to sd-agent:
`` `$ sudo service sd-agent restart` ``
and data will start to be reported to Server Density.

## Back to Server Density

### Alerting
#### Alerting on return values

Creating an alert when the server sensors triggers or returns a unknown state. The plugin will return 2 - CRITICAL or 3 - UNKNOWN:

1. *Alerts Tab*
2. _Add new alert_
3. Select the server reporting the data, fill in the alert form as desired
4. Select _Nagios Wrapper_ from the _Check pull_ down menu.
5. Use the Nagios plugin label for the key, in this case _check_sensors_
6. Setting the trigger to _Greater than or equal_ to 2

#### Alerting on performance values

Creating an alert when the mail queue is not zero:

1. *Alerts Tab*
2. _Add new alert_
3. Select the server reporting the data, fill in the alert form as desired
4. Select _Nagios Wrapper_ from the _Check_ pull down menu.
5. Use the Nagios plugin label for the key, in this case _unsent_
6. Setting the trigger to _Greater than_ 0


#### Graphs
Automatically, Server Density will plot any of the reported values.

1. *Devices Tab*
2. Select the server reporting the data (we can see that the unsent mail queue is 1 and at 12:43 was 2)
![alt text](/img/graph.png "Plot")
