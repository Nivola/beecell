# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte


def is_string(data):
    res = False
    if isinstance(data, str) or isinstance(data, bytes):
        res = True
    return res


def is_int(s):
    """Check whether string s is a positive or negative integer

    :param s: the string to validate
    :return: boolean True o False
    """
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()