MongoDB Plugin
===

This plugin gets stats from a [MongoDB server](http://www.mongodb.com) 

Configuration
---
1. Set your mongoDB host and port, by default the plugin assumes 127.0.0.1 and 27017
2. Restart the agent.

Recommended alerts
---
* `lock_percent` - If this value is very high you may have be experiencing capacity problems with your server
* `connections_current` - This value shouldn't grow too much (ideally it should be under a few thousand connections in busy applications)
* `connections_available` - This value should never get to 0
* `opcounters_*` - This value indicates the activity of your server. It should be consistent with your app behavior
* `indexCounters_missRatioPS` - This value should be 0 or almost zero. Otherwise you're missing indexes
