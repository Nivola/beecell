#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2022 CSI-Piemonte

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
            'beecell',
            'beecell.amqp',
            'beecell.auth',
            'beecell.cache',
            'beecell.crypto_util',
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
            'beecell.sphinx.ext',
            'beecell.sqlalchemy',
            'beecell.swagger',
            'beecell.test',
            'beecell.tests',
            'beecell.tests.auth',
            'beecell.tests.db',
            'beecell.types',
        ],
        namespace_packages=[],
        py_modules=[
            'beecell.crypto',
            'beecell.file',
            'beecell.formatter',
            'beecell.__init__',
            'beecell.network',
            'beecell.password',
            'beecell.perf',
            'beecell.remote',
            'beecell.sendmail',
            'beecell.simple',
        ],
        classifiers=[
            'Development Status :: %s' % version,
            'Programming Language :: Python'
        ],
        entry_points={},
        data_files=[],
        package_dir={
            'beecell': 'beecell'
        },
        package_data={
            'beecell': ['VERSION']
        },
        install_requires=load_requires(),
        dependency_links=[],
        zip_safe=True,
        cmdclass={'install': install},
        keywords='',
        python_requires='',
        obsoletes=[],
    )
