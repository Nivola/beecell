# Changelog

## Versione 1.17.1 (?)
* Cryptography
  - rsa 2048
  - fernet module

## Version 1.16.0 (2024-03-26)
rilascio funzionalità

* Added
  - check tax_code
* Fixed
  - AMQP Client stop_ioloop_on_close=False
  - fixed is instead in in swagger helper
  - punctual import
  - Remove unused import
  - Sort import

## Version 1.15.3 (2024-03-11)
rilascio funzionalità

* Added
  - CacheClient with RedisManager: cahce client may use redis-sentinel or redis
* Fixed
  - fix bug sulle cache get keys
  - fix bug in cache delete

## Version 1.15.0 (2025-10-12)
rilascio funzionalità

* Added
  - setup debug for  code/debugpy
  - new environment vars for checks and info
* Fixed
  - obscure data utility function
  - checkemail utility function
  - timeout

## Version 1.14.0 (2023-06-22)
rilascio funzionalità

* Added
  - is_name and is_uuid check methods
  - added identity manager Class
* Fixed
  - Mailer send with no files attached
  - log elasticsearch rename client
  - send email fix multiple recipients
  - time and timeout optimization

## Version 1.13.0 (2023-02-24)
rilascio funzionalità

* Fixed
  - minor changes

## Version 1.12.0 (2023-01-27)
rilascio funzionalità

* Fixed
  - minor changes

## Version 1.11.0 (2022-10-11)

Rilascio nuove funzionalità
* Fixed
  - Various bugfixes

## Version 1.9.0 (2022-02-11)
rilascio funzionalità

* Added
  - add method split_string_in_chunks in simple
  - add method setex in RedisManager
  - add package crypto_util and class RasCrypto that manage asymmetric cryptography with rsa
  - add manage_connection in SqlManager
  - add method compile_query
  - add K8shHandler to manage new line when logging an exception and read from filebeat
* Fixed
  - improved import in simple module
  - moved read_file in file module to improve load performance
  - moved password methods in password module to improve load performance
  - moved dict, list, string, date methods in types package to improve load performance
  - moved cryptography methods in crypto module to improve load performance
  - correct RedisManager timeout setting. socket_timeout was not from param and default value of 0.1s is too low
  - removed in ldap.authenticate code for reconnection. code is bad and bypass wrong password
  - Various bugfixes

## Version 1.8.0 (2021-06-11)
rilascio funzionalità

* Added
  - add support connection using ssh tunnel to paramiko_shell
  - add rsync client authentication with ssh key
  - add management of redis cluster with sentinel
  - add tunnel configuration for sql manager
  - add method exec_statements in sql manager
* Fixed
  - fixed parse_redis_uri to parse redis sentinel uri
  - replaced character | with + in simple.truncate
  - renamed schema in db in SqlManager

## Version 1.7.1 (2021-02-05)
rilascio correttive

* Added
  - added command ParamikoShell scp to exec secure copy
  - added class Rsync to run rsync between folder
  - add MysqlManager methods show_binary_log and purge_binary_log to manage binary logs
  - add method validate_string
* Fixed
  - correct some bugs in ParamikoShell: exit sometimes was not captured, command trace run twice.

  - correct connection release in MysqlManager
  - correct User._check_password
  - change method LdapAuth.authenticate to authenticate(self, username, password, max_retry=3, cur_retry=0). Add param
  - max_retry to manage some connections retry to ldap
  - update Copyright to 2020-2021
  - Various bugfixes
* Removed
  - removed cement_cmd package. Compatible only with python 2
  - removed module server.gevent_ssl
  - removed test for redis cluster

## Version 1.7.0 (2020-12-31)
rilascio funzionalità

* Added
  - added mysql manager methods to manage mysql replica
  - added methods get_line, get_pretty_size
  - add ParamikoShell commands mkdir, chown, chmod
* Fixed
  - correct some bugs in ParamikoShell: exit sometimes was not captured, command trace run twice.

  - correct connection release in MysqlManager
  - correct User._check_password
  - update Copyright to 2020-2021
* Removed
  - removed cement_cmd package. Compatible only with python 2
  - removed module server.gevent_ssl
  - removed test for redis cluster

## Version 1.6.1 (2020-06-21)
rilascio funzionalità

* Added
  - added syslog_handler
  - add CacheClient method get_by_pattern
* Fixed
  - fixed some bugs

## Version 1.6.0 (2019-11-08)
rilascio funzionalità

* Added
  - add method multi_get
  - add method is_string
* Fixed
  - bug on redis-cluster run_cmd that does not return results if connection to redis cluster fails
  - changed timeout in ParamikoShell from 1.0 to 10.0 seconds

## Version 1.5.0 (2019-09-04)
rilascio funzionalità

* Added
  - add scan method to RedisManager
  - add method prefixlength_to_netmask
  - module network
  - added logger for elasticsearch
* Fixed
  - Various bugfixes
  - requirements update

## Version 1.4.0 (2019-05-34)
rilascio funzionalità

* Added
  - cache manager based on redis
* Fixed
  - corrected parameters of database session creation. Set autoflush=True and expire_on_commit=True
  - modify class auth.LdapAuth. Now login workflow has the following steps ldap login using a  system user, query
  - ldap for user existence, get user dn, ldap login using user dn and password

## Version 1.3.0 (2019-02-27)
rilascio funzionalità

* Added
  - test runner to use with concurrent unit test
* Fixed
  - Various bugfixes

## Version 1.2.0 (2019-02-01)
rilascio funzionalità

* Fixed
  - Various bugfixes
  - changed method **random_password*- to create a more stronger password

## Version 1.1.0 (2019-01-13)
rilascio funzionalità

* Added
  - added methods simple.dict_get, simple.dict_set
* Fixed
  - Various bugfixes

## Version 1.0.0 (2018-07-31)

Rilascio nuove funzionalità

## Version 0.1.0 (2016-04-18)
First private preview release.

