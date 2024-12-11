# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

with open("%sVERSION" % __file__.replace("__init__.py", "")) as f:
    __version__ = f.read()

__git_last_commit__ = ""
try:
    import os

    LAST_COMMIT_PATH = os.getenv("LAST_COMMIT_BEECELL")
    if LAST_COMMIT_PATH is not None:
        with open(LAST_COMMIT_PATH) as f:
            __git_last_commit__ = f.read()
except Exception as ex:
    print(ex)
    pass
