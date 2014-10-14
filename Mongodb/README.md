MongoDB Plugin
===

This plugin gets stats from a [MongoDB server](http://www.mongodb.com) 

Requirements
---
* Pymongo

Configuration
---
1. Set your mongoDB host and port, by default the plugin assumes 127.0.0.1 and 27017. To do so use the agent configuration entry: mongodb_plugin_server.
Example: 127.0.0.1:27017
2. Define if the individual database stats are to be collected with the agent configuration entry mongodb_plugin_dbstats with value "yes" 
3. Restart the agent.

Parameters
---
All parameters must be in the MongoDB section of the configuration file
* `mongodb_plugin_server` - MongoDB server host and port in the format host:port
* `mongodb_plugin_dbstats` - Define if the individual database metrics are to be collected. The metrics will be collected if the value is "yes"
* `mongodb_plugin_replset` - Replica set configuration is collected if the value is "yes"
Example:

```
[MongoDB]
mongodb_plugin_server: 127.0.0.1:27017
mongodb_plugin_dbstats: yes
mongodb_plugin_replset: no
```

Recommended alerts
---
* `lock_percent` - If this value is very high you may have be experiencing capacity problems with your server
* `connections_current` - This value shouldn't grow too much (ideally it should be under a few thousand connections in busy applications)
* `connections_available` - This value should never get to 0
* `opcounters_*` - This value indicates the activity of your server. It should be consistent with your app behavior
* `indexCounters_missRatioPS` - This value should be 0 or almost zero. Otherwise you're missing indexes
