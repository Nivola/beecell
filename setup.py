#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

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


def load_requires():
    with open('./MANIFEST.md') as f:
        requires = f.read()
    return requires


def load_version():
    with open('./beecell/VERSION') as f:
        version = f.read()
    return version


if __name__ == '__main__':
    version = load_version()
    setup(
        name='beecell',
        version=version,
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
            'Development Status :: %s' % version,
            'Programming Language :: Python'
        ],
        entry_points={},
        data_files=[
            ('.', ['beehive/VERSION']),
        ],
        package_data={},
        install_requires=load_requires(),
        dependency_links=[],
        zip_safe=True,
        cmdclass={'install': install},
        keywords='',
        python_requires='',
        obsoletes=[],
    )
