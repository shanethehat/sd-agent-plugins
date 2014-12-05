Redis Monitor
===
This plugin is for [Redis](https://www.redis.io/). It is based on the
detailed list of metrics available from the INFO command [Redis Commands](http://redis.io/commands/info).

Setup
---
This plugin uses the output from `redis-cli` using the `info` to collect data about all the available Redis databases.

Metrics
---

Recommended alerts
---

Configuration
---
[Redis]
host: localhost
port: 6379
dbs: 0,1
