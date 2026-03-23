# Changelog

## Version 1.18.2 (2026-03-12)

Rilascio nuove funzionalità
* Risolto
  - remove obsolete package directory references from setup.py

## Version 1.18.1 (2026-02-12)

Rilascio nuove funzionalità
* Aggiunto
  - Update licensing header
  - Update requirement
* Risolto
  - bugfix test oid (. valid in names)

## Version 1.18.0 (2026-01-22)

Rilascio nuove funzionalità
* Aggiunto
  - public ip and subnet functions
  - Implement minimal ColoredFormatter
* Risolto
  - updated python version, labraries and dependencies
  - schema definitions
  - recursive_update, added checks for edge cases
  - ldap auth lowered max_retries, close connection on errors
  - avoid sql injection
  - paramiko_shell log
* Rimosso
  - unused files
  - six direct usage

## Version 1.17.13 (2025-12-11)

Rilascio nuove funzionalità
* Risolto
  - fix haproxy typed dict

## Version 1.17.12 (2025-11-27)

Rilascio nuove funzionalità
* Aggiunto
  - staas_ontap_v2 goldencopy management for shared volumes
  - lbaas types
  - added NullCacheClient to support no cache configuration in a transparent way
* Risolto
  - type hints and exception logic

## Version 1.17.11 (2025-11-06)

Rilascio nuove funzionalità
* Risolto
  - fix ColoredFormatter

## Version 1.17.10 (2025-10-09)

Rilascio nuove funzionalità
* Risolto
  - db name utility

## Version 1.17.7 (2025-08-05)

Rilascio nuove funzionalità
* Aggiunto
  - SecurityGroup rule apply to NSX security group not to NSX distribuited firewall

## Version 1.17.3 (2025-03-28)

Rilascio nuove funzionalità
* Aggiunto
  - option to sql pool engine

## Version 1.17.2 (2025-03-12)

Rilascio nuove funzionalità

## Version 1.17.1 (2025-02-27)

Rilascio nuove funzionalità

## Version 1.17.0 (2025-02-24)
rilascio funzionalità

* Aggiunto
  - staas_ontap_v2
  - try_cast_to_ip, try_cast_to_network utils
  - robust variant read_file_v2 function
  - test failfast default True
  - type hints, lazy logging, general linting
  - byteorder in Fernet
* Risolto
  - get_session_advanced by specifying autocommit and autoflush
  - key management Use sha512 method signature and salt optional in sha512_crypt
  - Merge remote-tracking branch 'origin/wip/staas_ontap_v2' into stage
  - set version 1.17.0
  - Merge remote-tracking branch 'origin/wip/staas_ontap_v2' into stage
  - Merge remote-tracking branch 'origin/test' into stage
  - Merge remote-tracking branch 'origin/preprod' into devel
  - scp and other ssh nodes family commands fixed to work on private cloud passing through bastion
  - Changes to use encrypted passwords in env files
  - marshmallow plugin as global because of optional view dependencies
  - Merge remote-tracking branch 'origin/preprod' into stage
  - Add method to get class full name
  - expand user in filename to support path with ~
  - function validate_service_name.
  - Update package files
  - CacheClient add get_keys_by_pattern
* Rimosso
  - Remove bcrypt dependency

## Version 1.16.0 (2024-03-26)
rilascio funzionalità

* Aggiunto
  - check tax_code
* Risolto
  - AMQP Client stop_ioloop_on_close=False
  - fixed is instead in in swagger helper
  - punctual import
  - Remove unused import
  - Sort import

## Version 1.15.3 (2024-03-11)
rilascio funzionalità

* Aggiunto
  - CacheClient with RedisManager: cahce client may use redis-sentinel or redis
* Risolto
  - fix bug sulle cache get keys
  - fix bug in cache delete

## Version 1.15.0 (2025-10-12)
rilascio funzionalità

* Aggiunto
  - setup debug for  code/debugpy
  - new environment vars for checks and info
* Risolto
  - obscure data utility function
  - checkemail utility function
  - timeout

## Version 1.14.0 (2023-06-22)
rilascio funzionalità

* Aggiunto
  - is_name and is_uuid check methods
  - added identity manager Class
* Risolto
  - Mailer send with no files attached
  - log elasticsearch rename client
  - send email fix multiple recipients
  - time and timeout optimization

## Version 1.13.0 (2023-02-24)
rilascio funzionalità

* Risolto
  - minor changes

## Version 1.12.0 (2023-01-27)
rilascio funzionalità

* Risolto
  - minor changes

## Version 1.11.0 (2022-10-11)

Rilascio nuove funzionalità
* Risolto
  - Various bugfixes

## Version 1.9.0 (2022-02-11)
rilascio funzionalità

* Aggiunto
  - add method split_string_in_chunks in simple
  - add method setex in RedisManager
  - add package crypto_util and class RasCrypto that manage asymmetric cryptography with rsa
  - add manage_connection in SqlManager
  - add method compile_query
  - add K8shHandler to manage new line when logging an exception and read from filebeat
* Risolto
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

* Aggiunto
  - add support connection using ssh tunnel to paramiko_shell
  - add rsync client authentication with ssh key
  - add management of redis cluster with sentinel
  - add tunnel configuration for sql manager
  - add method exec_statements in sql manager
* Risolto
  - fixed parse_redis_uri to parse redis sentinel uri
  - replaced character | with + in simple.truncate
  - renamed schema in db in SqlManager

## Version 1.7.1 (2021-02-05)
rilascio correttive

* Aggiunto
  - added command ParamikoShell scp to exec secure copy
  - added class Rsync to run rsync between folder
  - add MysqlManager methods show_binary_log and purge_binary_log to manage binary logs
  - add method validate_string
* Risolto
  - correct some bugs in ParamikoShell: exit sometimes was not captured, command trace run twice.

  - correct connection release in MysqlManager
  - correct User._check_password
  - change method LdapAuth.authenticate to authenticate(self, username, password, max_retry=3, cur_retry=0). Add param
  - max_retry to manage some connections retry to ldap
  - update Copyright to 2020-2021
  - Various bugfixes
* Rimosso
  - removed cement_cmd package. Compatible only with python 2
  - removed module server.gevent_ssl
  - removed test for redis cluster

## Version 1.7.0 (2020-12-31)
rilascio funzionalità

* Aggiunto
  - added mysql manager methods to manage mysql replica
  - added methods get_line, get_pretty_size
  - add ParamikoShell commands mkdir, chown, chmod
* Risolto
  - correct some bugs in ParamikoShell: exit sometimes was not captured, command trace run twice.

  - correct connection release in MysqlManager
  - correct User._check_password
  - update Copyright to 2020-2021
* Rimosso
  - removed cement_cmd package. Compatible only with python 2
  - removed module server.gevent_ssl
  - removed test for redis cluster

## Version 1.6.1 (2020-06-21)
rilascio funzionalità

* Aggiunto
  - added syslog_handler
  - add CacheClient method get_by_pattern
* Risolto
  - fixed some bugs

## Version 1.6.0 (2019-11-08)
rilascio funzionalità

* Aggiunto
  - add method multi_get
  - add method is_string
* Risolto
  - bug on redis-cluster run_cmd that does not return results if connection to redis cluster fails
  - changed timeout in ParamikoShell from 1.0 to 10.0 seconds

## Version 1.5.0 (2019-09-04)
rilascio funzionalità

* Aggiunto
  - add scan method to RedisManager
  - add method prefixlength_to_netmask
  - module network
  - added logger for elasticsearch
* Risolto
  - Various bugfixes
  - requirements update

## Version 1.4.0 (2019-05-34)
rilascio funzionalità

* Aggiunto
  - cache manager based on redis
* Risolto
  - corrected parameters of database session creation. Set autoflush=True and expire_on_commit=True
  - modify class auth.LdapAuth. Now login workflow has the following steps ldap login using a  system user, query
  - ldap for user existence, get user dn, ldap login using user dn and password

## Version 1.3.0 (2019-02-27)
rilascio funzionalità

* Aggiunto
  - test runner to use with concurrent unit test
* Risolto
  - Various bugfixes

## Version 1.2.0 (2019-02-01)
rilascio funzionalità

* Risolto
  - Various bugfixes
  - changed method **random_password*- to create a more stronger password

## Version 1.1.0 (2019-01-13)
rilascio funzionalità

* Aggiunto
  - added methods simple.dict_get, simple.dict_set
* Risolto
  - Various bugfixes

## Version 1.0.0 (2018-07-31)

Rilascio nuove funzionalità

## Version 0.1.0 (2016-04-18)
First private preview release.

