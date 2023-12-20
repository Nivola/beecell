# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte


def merge_list(*list_args):
    """Given any number of lists, merge into a new list.

    :param *list_args arbitrary number of list (1 to N)
    :return list
    """
    result = []
    for list_arg in list_args:
        result.extend(list_arg)
    return result
