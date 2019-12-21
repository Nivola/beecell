# beecell
__beecell__ is a project that contains various python 2 utility modules. Utility are useful to manage password, connect to a sql db
and manage a remote ssh connection.

Here a more specific description of packages and modules.

Utility file that include variuos function:
- __simple.py__: general function for password encryption and decryption, dictionary utility, print data etc.
- __remote.py__: varius class create remote client, run ssh command, run tcp command, make http request, install software in a remote portal

Utility package:
- __paramiko_shell__: Python implementation of SSHv2. This package run and interactive shell and offers utility to handle it
- __networkx__: utility for handle  network
- __db__: database manager for mysql, postgress and redis
- __auth__: authentication manager based on database and on ldap
- __logger__: logging helper
- __cement_cmd__: cement 2 (https://pypi.org/project/cement/2.2.2/) extensions

## Prerequisites
Fundamental requirements is python 2.7.

First of all you have to install some package:

```
$ sudo apt-get install gcc
$ sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
```

At this point create a virtual env

```
$ virtualenv venv
$ source venv/bin/activate
```

## Installing

```
$ pip install git+https://github.com/Nivola/beecell.git
```

## Running the tests
Results of vulnerability assessment and/or penetration test.

- Activate virtual env

```
$ source venv/bin/activate
```

- Open tests directory __beecell/tests__
- Copy file beecell.yml in your home directory. Open the file and set correctly all the <BLANK> variables.
- Run some tests:

```
$ python sendmail.py
$ python cement_cmd.py 
$ python paramiko_shell.py 
$ python networkx_layout.py
$ python db/manager_mysql.py 
$ python db/manager_redis.py
$ python db/manager_redis_cluster.py 
$ python auth/perm.py 
$ python auth/ldap_auth.py 
$ python auth/database_auth.py 
```

## Versioning
We use Semantic Versioning for versioning. (http://semver.org)

## Authors and Contributors
See the list of contributors who participated in this project in the file AUTHORS.md contained in each specific project.

## Copyright
CSI Piemonte - 2018-2019
CSI Piemonte - 2019-2020

## License
See the LICENSE.txt file for details
