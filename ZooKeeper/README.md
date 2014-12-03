ZooKeeper Plugin
===

This plugin gets stats from a [ZooKeeper server](http://zookeeper.apache.org/)

Configuration
---

Parameters
---
* `host` - Zoo Keeper hostname
* `port` - Port number Zoo Keeper runs on

Example:

```
[ZooKeeper]
host: 127.0.0.1
port: 2181
```

Recommended alerts
---

* `ruok` - This should be 0, if ZooKeeper isn't or it doesn't respond it will go to 1.