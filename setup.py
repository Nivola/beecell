#!/usr/bin/env python
# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

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
    with open("./MANIFEST-ansible.md") as f:
        requires = f.read()
    return requires


def load_version():
    with open("./beecell/VERSION") as f:
        version = f.read().rstrip()
    return version


if __name__ == "__main__":
    version = load_version()
    setup(
        name="beecell",
        version=version,
        description="Utility",
        long_description="Utility",
        long_description_content_type="text/plain",
        author="CSI Piemonte",
        author_email="nivola.engineering@csi.it",
        license="EUPL-1.2",
        url="",
        scripts=[],
        packages=[
            "beecell",
            "beecell.auth",
            "beecell.cache",
            "beecell.crypto_util",
            "beecell.db",
            "beecell.flask",
            "beecell.logger",
            "beecell.networkx",
            "beecell.paramiko_shell",
            "beecell.server",
            "beecell.server.uwsgi_server",
            "beecell.sphinx",
            "beecell.sphinx.ext",
            "beecell.sqlalchemy",
            "beecell.swagger",
            "beecell.test",
            "beecell.tests",
            "beecell.tests.auth",
            "beecell.tests.db",
            "beecell.types",
        ],
        namespace_packages=[],
        py_modules=[
            "beecell.crypto",
            "beecell.file",
            "beecell.formatter",
            "beecell.__init__",
            "beecell.network",
            "beecell.password",
            "beecell.remote",
            "beecell.sendmail",
            "beecell.simple",
        ],
        classifiers=[
            "Development Status :: %s" % version,
            "Programming Language :: Python",
        ],
        entry_points={},
        package_dir={"beecell": "beecell"},
        package_data={"beecell": ["VERSION"]},
        data_files=[('beecell', ["MANIFEST-ansible.md","MANIFEST.md"])],
        install_requires=load_requires(),
        dependency_links=[],
        zip_safe=True,
        cmdclass={"install": install},
        keywords="",
        python_requires="",
        obsoletes=[],
    )
