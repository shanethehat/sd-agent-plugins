Available Entropy
===
This plugin is for reporting status of "Available Entropy" on system.
Entropy is the measure of the random numbers available from /dev/urandom.

Used by: SSL connections, cryptographic services, etc.

**ONLY WORKS ON LINUX**

Setup
---
No special setup.

Metrics
---

Source: cat /proc/sys/kernel/random/entropy_avail

Recommended alerts
---

* `available` - Greater than 1000 (depends on your needs).

Random number generators (software)
---
[haveged](http://www.issihosts.com/haveged/)
[rng-tools](https://www.gnu.org/software/hurd/user/tlecarrour/rng-tools.html)

There are also packages for **yum** and **apt** available!
