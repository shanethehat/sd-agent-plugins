uWSGI Monitor
===

This plugin is for [uWSGI](http://uwsgi-docs.readthedocs.org/en/latest/).
It is based on the statistics available from the uwsgi stats server
[uWSGI stats server](http://uwsgi-docs.readthedocs.org/en/latest/StatsServer.html).


Setup
---
Start uWSGI with `--stats /tmp/stat.sock`.
Set the `socket_paths` option to point to the socket file.

> This plugin only supports Unix socket connection but could easily be extended
> to support TCP connections.


Metrics
---

Field                    |  Description                                                 | Type
------------------------ |  ----------------------------------------------------------- | ------
exception\_count         | Total number of exception raised across all workers          | Int
harakiri\_count          | Total number of non-responding workers killed                | Int
respawn\_count           | Total number of respawned processed                          | Int
request\_count           | Total number of processed requests                           | Int
request\_avg\_time       | Average time across all workers                              | Float
memory\_rss              | Total memory resident size across all workers                | Int
network\_tx              | Total bytes transfered across all workers                    | Int
workers\_count           | Total number of workers                                      | Int
workers\_busy\_count     | Total number of worker currently handling a request          | Int
workers\_cheap\_count    | Total number of available cheap worker                       | Int
workers\_idle\_count     | Number of available workers waiting for a request to process | Int


Recommended alerts
---


Configuration
---
[Uwsgi]
socket\_paths = /var/run/\*\_stats.sock,/tmp/test\_stats

> socket\_paths supports multiples comma-separated paths and path globbing.
