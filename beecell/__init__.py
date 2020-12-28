# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

import os.path
with open('%sVERSION' % __file__.replace('__init__.py', '')) as f:
    __version__ = f.read()

version_file = os.path.join(os.path.abspath(__file__).rstrip('__init__.pyc'), 'VERSION')
if os.path.isfile(version_file):
    with open(version_file) as version_file:
        __version__ = '%s-%s' % (__version__, version_file.read().strip()[:10])
