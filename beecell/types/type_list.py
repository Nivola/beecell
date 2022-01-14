# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte


def merge_list(*list_args):
    """Given any number of lists, merge into a new list.

    :param *list_args arbitrary number of list (1 to N)
    :return list
    """
    result = []
    for list_arg in list_args:
        result.extend(list_arg)
    return result