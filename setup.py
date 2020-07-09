#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte

from setuptools import setup
from setuptools.command.install import install as _install


class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()


if __name__ == '__main__':
    setup(
        name='beecell',
        version='1.6.1',
        description='Utility',
        long_description='Utility',
        author='CSI Piemonte',
        author_email='nivola.engineering@csi.it',
        license='GPL v3',
        url='',
        scripts=[],
        packages=[
            'beecell.amqp',
            'beecell.auth',
            'beecell.cache',
            'beecell.cement_cmd',
            'beecell.db',
            'beecell.db.mysql',
            'beecell.flask',
            'beecell.flask.login',
            'beecell.flask.login.bootstrap',
            'beecell.logger',
            'beecell.logger.server',
            'beecell.networkx',
            'beecell.paramiko_shell',
            'beecell.server',
            'beecell.server.uwsgi_server',
            'beecell.sphinx',
            'beecell.sqlalchemy',
            'beecell.swagger',
            'beecell.test',
            'beecell.tests',
            'beecell.tests.db',
            'beecell.tests.auth',
        ],
        namespace_packages=[],
        py_modules=[
            'beecell.simple',
            'beecell.perf',
            'beecell.sendmail',
            'beecell.remote',
            'beecell.formatter',
            'beecell.network',
            'beecell.__init__'
        ],
        classifiers=[
            'Development Status :: 1.6',
            'Programming Language :: Python'
        ],
        entry_points={},
        data_files=[],
        package_data={},
        install_requires=[
            "SQLAlchemy==1.3.17",
            "Flask==1.1.2",
            "Flask-Babel==1.0.0",
            "Flask-Login==0.5.0",
            "Flask-SQLAlchemy==2.4.1",
            "Flask-WTF==0.14.3",
            "Flask-Session==0.3.1",
            "anyjson==0.3.3",
            "pika==1.1.0",
            "Paramiko==2.6.0",
            "blessings==1.7.0",
            "pygments==2.4.2",
            "psutil==5.6.3",
            "PrettyTable==0.7.2",
            "redis==3.5.0",
            "passlib==1.7.1",
            "pymysql==0.9.3",
            "httplib2==0.18.1",
            "pymongo==3.9.0",
            "ujson==2.0.3",
            "hiredis==1.0.0",
            "#gevent==1.4.0",
            "gevent==20.5.0",
            "docutils==0.15.2",
            "python-ldap==3.2.0",
            "pyzmq==18.1.0",
            "os-client-config==1.32.0",
            "dicttoxml==1.7.4",
            "pyvmomi==6.7.1.2018.12",
            "oslo.utils==3.41.0",
            "easywebdav==1.2.0",
            "networkx==2.2",
            "cryptography==2.7",
            "celery==4.4.2",
            "kombu==4.6.8",
            "urllib3==1.25.7",
            "pyopenssl==19.0.0",
            "pycrypto==2.6.1",
            "xmltodict==0.12.0",
            "PyYAML==5.1.2",
            "proxmoxer==1.0.3",
            "geventhttpclient==1.3.1",
            "tabulate==0.8.3",
            "ipaddress==1.0.23",
            "ansible==2.8.4",
            "oauthlib==3.1.0",
            "requests_oauthlib==1.2.0",
            "pyjwt==1.7.1",
            "bcrypt==3.1.7",
            "apispec==3.3.0",
            "flasgger==0.9.4",
            "marshmallow==3.5.2",
            "apispec-webframeworks==0.5.2",
            "flex==6.14.0",
            "requests==2.22.0",
            "setuptools==41.2.0",
            "dnspython==1.16.0",
            "python-dateutil==2.8.0",
            "billiard==3.6.3.0",
            "elasticsearch==7.0.4",
            "six==1.14.0",
            "netapp_ontap==9.7.0"
        ],
        dependency_links=[],
        zip_safe=True,
        cmdclass={'install': install},
        keywords='',
        python_requires='',
        obsoletes=[],
    )
