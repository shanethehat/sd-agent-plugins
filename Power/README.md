Power Monitor
===

This plugin is for [lm-sensors](http://www.lm-sensors.org/) and Raspberry Pi.

Setup
---

Linux
---
1. You must have installed [lm-sensors](http://www.lm-sensors.org/).
2. Ensure the command `sensors` outputs the correct data.

Metrics
---
Power consumption in Ws

Recommended alerts
---
* `power*` - High usage, might indicate server is getting overloaded

Configuration
---
```
[Power]
adapters: 'fam15h_power-pci-00c4,fam15h_power-pci-00cc' # specify adapters to report on
```
