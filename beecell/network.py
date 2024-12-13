# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte

# https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml


class InternetProtocol(object):
    p_tcp = 6
    p_udp = 17
    p_icmp = 1
    p_icmp_echo = 0

    def get_name_from_number(self, number):
        proto = {str(getattr(self, x)): x for x in filter(lambda x: x.find("p_") == 0, dir(InternetProtocol))}
        name = proto.get(str(number), None)
        if name is not None:
            name = name[2:]
        return name

    def get_number_from_name(self, name):
        return getattr(self, "p_%s" % name, None)

    def get_names(self):
        proto = [
            {"proto": x[2:], "number": getattr(self, x)}
            for x in filter(lambda x: x.find("p_") == 0, dir(InternetProtocol))
        ]
        return proto
