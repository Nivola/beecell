# Changelog

## Version 1.6.0 (Sep , 2019)

* Added ...
    * add method to check python major version
    * add method multi_get
    * add method is_string
* Fixed ...
    * bug on redis-cluster run_cmd that does not return results if connection to redis cluster fails
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