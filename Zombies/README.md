Zombies Monitor
===
This plugin is for reporting number of "zombie" processes as report by the command line tool "top".

CURRENTLY ONLY WORKS ON LINUX.

Setup
---
No special setup except that you have "top" installed. This is usually installed by default.

Metrics
---
Number of zombie processes on the server, usually 0.

Recommended alerts
---

* `zombies` - Greater than zero. Nobody wants the undead wondering about their server...

Configuration
---
None
