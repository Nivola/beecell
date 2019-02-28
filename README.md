# beecell
Utility file that include variuos function:
- __simple.py__: general function for password encryption and decryption, dictionary utility, print data etc.
- __remote.py__: varius class create remote client, run ssh command, run tcp command, make http request, install software in a remote portal

Utility package:
- __paramiko_shell__: Python implementation of SSHv2. This package run and interactive shell and offers utility to handle it
- __networkx__: utility for handle  network 

## Prerequisites
First of all you have to install a virtual env and have python 2.7

```
$ virtualenv venv
$ source venv/bin/activate
```

At this poit install some package:

```
$ sudo apt-get install gcc
$ sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
```

## Installing

```
$ pip install git+https://clsk-code.csi.it/2076/beecell.git --trusted-host clsk-code.csi.it
```

## Getting Started
Instructions useful to deploy software on a simple environment (local machine or simple server configuration infrastructure).

## Running the tests (Optional)
Results of vulnerability assessment and/or penetration test. If known explain how to run the automated tests for this system


## Deployment (Optional)
Add additional notes about how to deploy this on a live system

## Versioning
We use Semantic Versioning for versioning. (http://semver.org)

## Authors and Contributors
beecell is written and maintained by: 

* Sergio Tonani
* Michele Bello
* Antonio Brasile
* Gianni Doria
* Daniela Ferrarini
* Dennis Sayed

## Copyrights
CSI Piemonte

## License
See the LICENSE.txt file for details
