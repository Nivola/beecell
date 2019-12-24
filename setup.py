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
        version='1.6',
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
            "sqlalchemy==1.3.11",
            "redis-py-cluster==2.0.0",
            "Flask==1.1.1",
            "anyjson==0.3.3",
            "psutil==5.6.3",
            "redis==3.0.1",
            "passlib==1.7.1",
            "pymysql==0.9.3",
            "ujson==1.35",
            "hiredis==1.0.0",
            "gevent==1.4.0",
            "PrettyTable==0.7.2",
            "paramiko==2.6.0",
            "httplib2==0.13.1",
            "urllib3==1.25.7",
            "pymongo==3.9.0",
            "pika==1.1.0",
            "Flask-Login==0.4.1",
            "cement==2.10.12",
            "WTForms==2.2.1",
            "Flask-WTF==0.14.2",
            "celery==4.2.2",
            "uwsgidecorators==1.1.0",
            "flex==6.14.0",
            "marshmallow==2.19.5",
            "apispec==0.38.0",
            "python-ldap==3.2.0",
            "PyYAML==5.1.2",
            "dict-recursive-update==1.0.1",
            "bcrypt==3.1.7",
            "networkx==2.2"
        ],
        dependency_links=[],
        zip_safe=True,
        cmdclass={'install': install},
        keywords='',
        python_requires='',
        obsoletes=[],
    )
