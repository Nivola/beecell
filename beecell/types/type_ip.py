# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte


def ip2cidr(ip_address):
    """

    :param ip_address:
    :return:
    """
    res = ip_address.split("/")
    if len(res) == 1:
        return "%s/32" % res[0]
    return ip_address
