Fan Speed Monitor
===

This plugin is for [lm-sensors](http://www.lm-sensors.org/).

Setup
---

Linux
---
1. You must have installed [lm-sensors](http://www.lm-sensors.org/).
2. Ensure the command `sensors` outputs the correct data.

Metrics
---
Speed of attached fans.

Recommended alerts
---
* `fan*` - Fan speed, if this suddenly decreases a fan might be broken or the load has increased.

Configuration
---
```
[FanSpeed]
ignore: 'fan2' # ignore fans not attached or not in use
```