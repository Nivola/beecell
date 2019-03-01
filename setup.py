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
        version='1.0',
        description='',
        long_description='',
        author='',
        author_email='',
        license='',
        url='',
        scripts=[],
        packages=[
            'beecell.flask',
            'beecell.paramiko_shell',
            'beecell.networkx',
            'beecell.amqp',
            'beecell.test',
            'beecell.cement_cmd',
            'beecell.sphinx',
            'beecell.sqlalchemy',
            'beecell.auth',
            'beecell.db',
            'beecell.tests',
            'beecell.server',
            'beecell.uwsgi_sys',
            'beecell.logger',
            'beecell.swagger',
            'beecell.flask.login',
            'beecell.flask.login.bootstrap',
            'beecell.amqp.simple',
            'beecell.sphinx.ext',
            'beecell.db.mysql',
            'beecell.server.uwsgi_server',
            'beecell.server.uwsgi_server.test1',
            'beecell.logger.server'
        ],
        namespace_packages=[],
        py_modules=[
            'beecell.simple',
            'beecell.dicttoxml',
            'beecell.perf',
            'beecell.test_util',
            'beecell.xml_parser',
            'beecell.sendmail',
            'beecell.remote',
            'beecell.webdav',
            '__init__',
            'beecell.tree'
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',
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
            "redis-collections==0.6.0",
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
