Server Density Plugins
===

These plugins are made freely available for various applications. [See the full list on our website](https://www.serverdensity.com/plugins).

Configuring the agent
---
The first time you install a plugin you need to set the agent up. After that, you can just drop a new plugin into the plugin directory, then restart the agent.

1. Create a directory where you want to store your plugins. The agent needs to have write access to this directory so we recommend the same location the agent is installed, usually `/usr/bin/sd-agent/plugins/`
2. Set the `plugin_directory` agent config value to the full path to this new directory e.g. `/usr/bin/sd-agent/plugins/`
3. Place any plugins into this new directory.
4. Restart the agent.

Troubleshooting plugins
---
[Place the agent into debug mode](https://support.serverdensity.com/hc/en-us/articles/200495543-Debug-mode-Linux-FreeBSD-Mac) and check [the logs](https://support.serverdensity.com/hc/en-us/articles/201244753-Agent-logs) to see what the plugin is doing.

You can see what is being sent back to us from the "Plugins" tab when viewing the device in the Server Density web UI.

If you have problems, [e-mail us](hello@serverdensity.com).
