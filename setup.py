#!/usr/bin/env python

# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

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
        version='1.3',
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
            'beecell.cement_cmd',
            'beecell.db',
            'beecell.flask',
            'beecell.flask.login',
            'beecell.flask.login.bootstrap',
            'beecell.logger',
            'beecell.logger.server',
            'beecell.networkx',
            'beecell.paramiko_shell',
            'beecell.server',
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
            '__init__'
        ],
        classifiers=[
            'Development Status :: 1.3',
            'Programming Language :: Python'
        ],
        entry_points={},
        data_files=[],
        package_data={},
        install_requires=[
            "SQLAlchemy==1.2.8",
            "redis-py-cluster==1.3.6",
            "Flask==1.0.2",
            "anyjson==0.3.3",
            "psutil==5.4.6",
            "redis==2.10.6",
            "passlib==1.7.1",
            "pymysql==0.8.1",
            "ujson==1.35",
            "hiredis==0.2.0",
            "gevent==1.3.4",
            "PrettyTable==0.7.2",
            "paramiko==2.4.2",
            "httplib2==0.12.0",
            "urllib3==1.24.1",
            "pymongo==3.7.2",
            "pika==0.13.0",
            "flask-login",
            "cement==2.10.12",
            "WTForms==2.2.1",
            "Flask-WTF",
            "celery==4.2.1",
            "springpython==1.3.0.RC1",
            "uwsgidecorators==1.1.0",
            "flex==6.14.0",
            "apispec==1.0.0",
            "marshmallow==2.18.1",
            "python-ldap==3.1.0",
            "PyYAML==3.12",
            "dict-recursive-update==1.0.1",
            "bcrypt==3.1.4"
        ],
        dependency_links=[],
        zip_safe=True,
        cmdclass={'install': install},
        keywords='',
        python_requires='',
        obsoletes=[],
    )
