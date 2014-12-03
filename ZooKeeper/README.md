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

* `imok` - This should be 0, if ZooKeeper isn't or it doesn't respond it will go to 1.
* `zk_outstanding_requests` - This should be as low as possible, high values might some upgrades are needed.
* `latency avg` - Average latency, high values might mean slower than needed performance

Metrics
---
Below is an example payload returned by the plugin.

```
{
    "Connections": 1,
    "Node count": 19,
    "Outstanding": 0,
    "Received": 101950,
    "Sent": 102016,
    "clientPort": 2181,
    "imok": 0,
    "latency avg": 0,
    "latency max": 751,
    "latency min": 0,
    "maxClientCnxns": 60,
    "maxSessionTimeout": 40000,
    "minSessionTimeout": 4000,
    "serverId": 0,
    "tickTime": 2000,
    "zk_approximate_data_size": 430,
    "zk_avg_latency": 0,
    "zk_ephemerals_count": 0,
    "zk_max_file_descriptor_count": 10240,
    "zk_max_latency": 751,
    "zk_min_latency": 0,
    "zk_num_alive_connections": 1,
    "zk_open_file_descriptor_count": 37,
    "zk_outstanding_requests": 0,
    "zk_packets_received": 101951,
    "zk_packets_sent": 102017,
    "zk_server_state": 0, # 0 == standalone
    "zk_watch_count": 0,
    "zk_znode_count": 19
}
```

Configuration
---
```
[ZooKeeper]
host: localhost
port: 2181