# beecell
__beecell__ is a project that contains various python 3 utility modules. Utility are useful to manage password, connect 
to a sql db and manage a remote ssh connection.

Here a more specific description of packages and modules.

Utility file that include variuos function:
- __simple.py__: general function for password encryption and decryption, dictionary utility, print data etc.
- __remote.py__: various class create remote client, run ssh command, run tcp command, make http request, install 
  software in a remote portal

Utility package:
- __paramiko_shell__: Python implementation of SSHv2. This package run and interactive shell and offers utility to 
  handle it
- __networkx__: utility for handle  network
- __db__: database manager for mysql, postgress and redis
- __auth__: authentication manager based on database and on ldap
- __logger__: logging helper

## Prerequisites
Fundamental requirements is python 3.7>.

First of all you have to install some package and create a python virtual env:

```
$ sudo apt -y install gcc python-dev sshpass rsync mariadb-client git libldap2-dev libffi-dev libssl-dev libsasl2-dev pkg-config libvirt-dev
$ python3 -m venv /tmp/py3-test-env
$ source /tmp/py3-test-env/bin/activate
```

## Installing

Public packages:

```
$ pip install -U git+https://github.com/Nivola/beecell.git
```

CSI Internal packages:

```
$ pip3 install -U git+https://gitlab.csi.it/nivola/cmp3/beecell.git@devel
```

## Running the tests
Activate virtual env

```
$ source /tmp/py3-test-env/bin/activate
```

Open tests directory __beecell/tests__. Copy file beecell.yml in your home directory. Open the file and set correctly 
all the <BLANK> variables.

### Run some tests:

```
$ python sendmail.py
$ python paramiko_shell.py 
$ python networkx_layout.py
$ python db/manager_mysql.py 
$ python db/manager_redis.py
$ python auth/perm.py 
$ python auth/ldap_auth.py 
$ python auth/database_auth.py 
```

Test log can be seen in the home directory. 
Files: 
- __test.log__

## Versioning
We use Semantic Versioning for versioning. (https://semver.org)

## Authors and Contributors
See the list of contributors who participated in this project in the file AUTHORS.md contained in each specific project.

## Copyright
CSI Piemonte - 2018-2021

## License
See the LICENSE.txt file for details
