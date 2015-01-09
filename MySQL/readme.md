# MySQL monitoring  - Linux, Mac and FreeBSD

## 1. Dependencies

Our MySQL plugin uses MySQLdb module to interact with MySQL. You must have this installed to use the MySQL monitoring functionality.

a) Installation - package managed (try this first)

CentOS, Fedora, RHEL:

    yum install python-devel
    yum install MySQL-python

Debian, Ubuntu:

    apt-get install python-dev
    apt-get install python-mysqldb

b) Installation - manual (try this if option a) above does not work)

Download MySQLdb and install it: This will require the Python build tools and MySQL development headers.

    python setup.py build
    python setup.py install

You will also need to set the permissions if you installed the agent using our OS packages: 

    chmod -R 777 /usr/bin/sd-agent/

c) Installation - manual (dependancies)

If you get errors in step b) above, you may need to install some extra packages. Install the Python build tools and MySQL headers using your OS package management:

CentOS, Fedora, RHEL:

    yum install python-devel
    yum install mysql-devel

Debian, Ubuntu:

    apt-get install python-dev
    apt-get install mysql-devel
Then install the Python setuptools by following the instructions on the website. You will then be able to go back to step b).


## 2. Agent configuration

The agent /etc/sd-agent/config.cfg file requires 3 additional config lines to be completed to allow the agent to connect to your MySQL server. 

    [MySQLServer]
    mysql_server:
    mysql_user:
    mysql_pass:

Fill out the details for each line for a MySQL user. Your `mysql_server` will generally be `localhost` unless you want the agent to connect to a remote server.

    [MySQLServer]
    mysql_server: localhost
    mysql_user: my_username
    mysql_pass: my_password

### Custom ports and sockets
You can specify a custom port and/or socket if you are not running the default. You do this by adding 2 new config options to the config file underneath the existing options e.g, the default port is `3306`: 

    mysql_port: 3307
    mysql_socket: /tmp/mysql.sock

### Monitoring extra parameters
You can add further parameters to monitor if you would like by including the following two parameters. The metrics need to be comma-separated as below. `mysql_include_per_s` gives you the metric per second whereas `mysql_include` just gives you the counter. You can find the entire list of metrics here in the [MySQL manual](http://dev.mysql.com/doc/refman/5.1/en/server-status-variables.html#statvar_Slow_queries).

    mysql_include_per_s: Com_commit, Bytes_sent, Com_analyze
    mysql_include: Com_commit, Com_truncate

### Users

You can use any user to connect to the database. The user will need process privilege to be able to gather `Checkpoint age` from the command `'SHOW ENGINE INNODB STATUS'`. We recommend that you create a specific user with this privilege. See the [MySQL documentation for user management instructions](http://dev.mysql.com/doc/refman/5.1/en/user-account-management.html).


## 3. Restart agent

Restart the agent to start the monitoring. Using replication? Make sure you set up the right alerts.

## 4. Add graphs

Click the name of your server from the Devices list in your Server Density account then go to the Metrics tab. Click the + Graph button on the right then choose the MySQL metrics to display the graphs. The metrics will also be available to select when building dashboard graphs.

