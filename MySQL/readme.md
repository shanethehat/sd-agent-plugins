# Config Parameters

All parameters must be in the MySQL section of the configuration file. 

`mysql_plugin_server` - MySQL server host and port in the format:

    host:port

or 

[MySQLServer]
mysql_plugin_server: localhost
mysql_plugin_user: username
mysql_plugin_pass: password

# custom ports and sockets

mysql_plugin_port: 3306
mysql_plugin_socket: /tmp/mysql.sock
mysql_slave: true



[MongoDB]
mongodb_plugin_server: 127.0.0.1:27017
mongodb_plugin_dbstats: yes
mongodb_plugin_replset: no
