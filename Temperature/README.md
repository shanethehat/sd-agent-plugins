Temperature Monitor
===

This plugin is for [lm-sensors](http://www.lm-sensors.org/) and Raspberry Pi.

Setup
---

Linux
---
1. You must be using [lm-sensors](http://www.lm-sensors.org/).
2. Ensure the command `sensors` outputs the correct data.

Raspberry Pi
---
Have the file ```/sys/class/thermal/thermal_zone0/temp``` available to read.

Metrics
---
CPU and motherboard temperatues.

Recommended alerts
---
* `Core *` - CPU temperatues, if this suddenly spikes or increases a fan might be broken.
* `temp*` - Sensors on the mainboard, raised values might indicate air intake into the case is broken.

Configuration
---
```

[Temperature]
scale: c # temperature_scale: c(elsius) f(ahrenheit) k(elvin)
cpus: yes
other: yes
```