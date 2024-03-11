# Changelog

## Version 1.15.3 ( mar , 2024)

* Added ...
  - CacheClient with RedisManager: cahce client may use redis-sentinel or redis

* Added ...
  - fix bug sulle cache get keys
  - fix bug in cache delete


## Version 1.15.0

* Added ...
  * setup debug for  code/debugpy
  * new environment vars for checks and info


* Fixed ...
  * obscure data utility function
  * checkemail utility function
  * timeout


* Integrated ...

## Version 1.14.0

* Added ...
  * is_name and is_uuid check methods
  * added identity manager Class

* Fixed ...
  * Mailer send with no files attached
  * log elasticsearch rename client
  * send email fix multiple recipients
  * time and timeout optimization



* Integrated ...
## Version 1.13.0

* Added ...

* Fixed ...
  * minor changes

* Integrated ...

## Version 1.12.0

* Added ...

* Fixed ...
  * minor changes

* Integrated ...

## Version 1.11.0 (oct 11, 2022)
* Various bugfixes

## Version 1.9.0 (feb 11, 2022)

* Added ...
    * add method split_string_in_chunks in simple
    * add method setex in RedisManager
    * add package crypto_util and class RasCrypto that manage asymmetric cryptography with rsa
    * add manage_connection in SqlManager
    * add method compile_query
    * add K8shHandler to manage new line when logging an exception and read from filebeat
* Fixed ...
    * improved import in simple module
    * moved read_file in file module to improve load performance
    * moved password methods in password module to improve load performance
    * moved dict, list, string, date methods in types package to improve load performance
    * moved cryptography methods in crypto module to improve load performance
    * correct RedisManager timeout setting. socket_timeout was not from param and default value of 0.1s is too low
    * removed in ldap.authenticate code for reconnection. code is bad and bypass wrong password
* Integrated ...
* Various bugfixes
* Removed

## Version 1.8.0 (jun 11, 2021)

* Added ...
    * add support connection using ssh tunnel to paramiko_shell
    * add rsync client authentication with ssh key
    * add management of redis cluster with sentinel
    * add tunnel configuration for sql manager
    * add method exec_statements in sql manager
* Fixed ...
    * fixed parse_redis_uri to parse redis sentinel uri
    * replaced character | with + in simple.truncate
    * renamed schema in db in SqlManager
* Integrated ...
* Various bugfixes
* Removed

## Version 1.7.1 (Feb 05, 2021)

* Added ...
    * added command ParamikoShell scp to exec secure copy
    * added class Rsync to run rsync between folder
    * add MysqlManager methods show_binary_log and purge_binary_log to manage binary logs
    * add method validate_string
* Fixed ...
    * correct some bugs in ParamikoShell: exit sometimes was not captured, command trace run twice.
    * correct connection release in MysqlManager
    * correct User._check_password
    * change method LdapAuth.authenticate to authenticate(self, username, password, max_retry=3, cur_retry=0). Add param
      max_retry to manage some connections retry to ldap
* Integrated ...
    * update Copyright to 2020-2021
* Various bugfixes
* Removed
    * removed cement_cmd package. Compatible only with python 2
    * removed module server.gevent_ssl
    * removed test for redis cluster

## Version 1.7.0 (Dec 31, 2020)

* Added ...
    * added mysql manager methods to manage mysql replica
    * added methods get_line, get_pretty_size
    * add ParamikoShell commands mkdir, chown, chmod
* Fixed ...
    * correct some bugs in ParamikoShell: exit sometimes was not captured, command trace run twice.
    * correct connection release in MysqlManager
    * correct User._check_password
* Integrated ...
    * update Copyright to 2020-2021
* Various bugfixes
* Removed
    * removed cement_cmd package. Compatible only with python 2
    * removed module server.gevent_ssl
    * removed test for redis cluster

## Version 1.6.1 (Jun 21, 2020)

* Added ...
    * added syslog_handler
    * add CacheClient method get_by_pattern
* Fixed ...
* Integrated ...
* Various bugfixes
    * fixed some bugs

## Version 1.6.0 (Nov 08, 2019)

* Added ...
    * add method multi_get
    * add method is_string
* Fixed ...
    * bug on redis-cluster run_cmd that does not return results if connection to redis cluster fails
    * changed timeout in ParamikoShell from 1.0 to 10.0 seconds
* Integrated ...
* Various bugfixes

## Version 1.5.0 (Sep 04, 2019)

* Added ...
    * add scan method to RedisManager
    * add method prefixlength_to_netmask
    * module network
    * added logger for elasticsearch
* Fixed ...
* Integrated ...
    * requirements update
* Various bugfixes

## Version 1.4.0 (May 24, 2019)

* Added ...
    * cache manager based on redis
* Fixed ...
    * corrected parameters of database session creation. Set autoflush=True and expire_on_commit=True
* Integrated ...
    * modify class auth.LdapAuth. Now login workflow has the following steps: ldap login using a  system user, query
      ldap for user existence, get user dn, ldap login using user dn and password
* Various bugfixes


## Version 1.3.0 (February 27, 2019)

* Added ...
    * test runner to use with concurrent unit test
* Fixed ...
* Integrated ...
* Various bugfixes

## Version 1.2.0 (February 01, 2019)

* Added ...
* Fixed ...
* Integrated ...
    * changed method **random_password** to create a more stronger password
* Various bugfixes

## Version 1.1.0 (January 13, 2019)

* Added ...
    * added methods simple.dict_get, simple.dict_set
* Fixed ...
* Integrated ...
* Various bugfixes

## Version 1.0.0 (July 31, 2018)

First production preview release.

## Version 0.1.0 (April 18, 2016)

First private preview release.