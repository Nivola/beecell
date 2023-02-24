# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

with open("%sVERSION" % __file__.replace("__init__.py", "")) as f:
    __version__ = f.read()
