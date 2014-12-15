ProFtpd Connection Reporting
===
This plugin is for reporting the user and connection count of proftpd.

For connection reportings **proftpd** with **ftpwho** is required.

**ONLY WORKS ON LINUX**

Setup
---

On errors, check your proftpd configuration or scoreboard file.

You can pass them with the following parameters to ftpwho:
```
  -c, --config
    specify full path to proftpd configuration file
  -f, --file
    specify full path to scoreboard file
```

Metrics
---

Taken from ftpwho:

```
{
    "Proftpd": {
        "connections": 5,
        "users": 2
    }
}
```

Note: There is currently no distinction between: idle, read, write, etc.

Recommended alerts
---

No alerts, just reporting.

Tests
---

This plugin was tested with: ProFTPD 1.3.6rc1 (git) (built Fri Dec 12 2014 20:19:19 UTC) standalone mode STARTUP on Ubuntu 14.04.1
