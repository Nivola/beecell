# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte


class StringFormatter(object):
    map = [
        ("'", '&#39;'),
        ('\"', '&#34;'),
        ('\\', '&#92;'),
        ('(', '&#40;'),
        (')', '&#41;'),
        ('{', '&#123;'),
        ('}', '&#125;'),
        ('\n', ' | '),
    ]

    def replace(self, message):
        for m in self.map:
            message = message.replace(*m)
        return message
