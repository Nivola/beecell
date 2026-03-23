# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte


class StringFormatter(object):
    """
    string formatter safe for html
    possibly unused
    """
    map = [
        ("'", "&#39;"),
        ('"', "&#34;"),
        ("\\", "&#92;"),
        ("(", "&#40;"),
        (")", "&#41;"),
        ("{", "&#123;"),
        ("}", "&#125;"),
        ("\n", " | "),
    ]

    def replace(self, message: str):
        """
        for each tuple in self.map, replaces
        the first element with the second
        """
        for m in self.map:
            message = message.replace(*m)
        return message
