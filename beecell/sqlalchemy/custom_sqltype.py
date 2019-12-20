# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte

import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator
from beecell.simple import isNotBlank


class TextDictType(TypeDecorator):
    impl = sqlalchemy.Text()

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        else:
            value = u'{}'
        return value

    def process_result_value(self, value, dialect):
        if isNotBlank(value):
            value = json.loads(value)
        else:
            value = {}
        return value
