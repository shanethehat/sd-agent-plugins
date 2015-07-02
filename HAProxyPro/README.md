HAProxy Plugin
===

This plugin gets stats from a [HAProxy server](http://www.haproxy.org/)

Configuration
---
1. This plugin uses a new section of the configuration file called ```HAProxyPro```. All the configuration entries should be in it for the plugin to read them.
2. Set your HAProxy host and port
Example: ``haproxy_url: http://USER:PASS@localhost:8080/clusterstats``
3. Restart the agent.

Config Parameters
---
All parameters must be in the HAProxyPro section of the configuration file
* `haproxy_url` - HAProxy server host and port in the format:
```
http://USER:PASS@localhost:8080/clusterstats
```
Example:

```
[HAProxyPro]
haproxy_url: http://USER:PASS@localhost:8080/clusterstats
```

## Acknowledgements

This plugin was originally developed by [@rex](https://github.com/rex/).
