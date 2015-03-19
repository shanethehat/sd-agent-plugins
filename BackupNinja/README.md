BackupNinja Monitor
===

This plugin is for [backupninja](https://labs.riseup.net/code/projects/backupninja/).

Recommended alerts
---
* `age` - Minutes since last backup run, -1 if unknown.
* `actions` - Number of backup actions executed.
* `error` - Number of actions that had an error.
* `fatal` - Number of actions that had a fatal error.
* `warning` - Number of actions that had a warning.

Configuration
---
```
[BackupNinja]
main_log: /var/log/backupninja.log
# sequence or date
rotated_log_type: sequence
```
