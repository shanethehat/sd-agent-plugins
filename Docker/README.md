Docker Monitor
===
This plugin is for [Docker](https://www.docker.com/). It is based on the
detailed list of metrics mentioned on [Docker Run Metrics](https://docs.docker.com/articles/runmetrics/).

Setup
---
This plugin uses the output from `sudo docker ps -l --no-trunc` to collect data about all the running containers.

Metrics
---
Any container on this wil be reported using available data from `/sys/fs/cgroup/`. The following list of files contain the statistics reported by the agent:

* /sys/fs/cgroup/memory/docker/{CONTAINER_ID}/memory.stat
* /sys/fs/cgroup/memory/docker/{CONTAINER_ID}/memory.oom_control
* /sys/fs/cgroup/cpu/docker/{CONTAINER_ID}/cpu.stat
* /sys/fs/cgroup/cpu/docker/{CONTAINER_ID}/blkio.sectors
* /sys/fs/cgroup/cpu/docker/{CONTAINER_ID}/blkio.io_service_bytes
* /sys/fs/cgroup/cpu/docker/{CONTAINER_ID}/blkio.io_serviced
* /sys/fs/cgroup/blkio/docker/{CONTAINER_ID}/blkio.io_queued

Recommended alerts
---
Below are three possible alerts that you might want to use. A lot of data is returned so we recommend you read
[Docker Run Metrics](https://docs.docker.com/articles/runmetrics/). This page has a detailed explaination of the stats we collect
and their meaning and possible impact on the hosting server.

* `memory-oom_control` - Changes to 1 if Out Of Memory Killer is active meaning processes will start to be killed.
* `memory-rss` - Amount of memory not used by stacks, heaps etc. Slow increase could mean a memory leak.
* `blkio-io_queued` - I/O operations currently queued. High numbers mean high amount of disk access.

Configuration
---
None
