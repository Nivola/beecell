# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator
from beecell.types.type_string import is_not_blank
from beecell.simple import jsonDumps


class TextDictType(TypeDecorator):
    impl = sqlalchemy.Text()

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = jsonDumps(value)
        else:
            value = '{}'
        return value

    def process_result_value(self, value, dialect):
        if is_not_blank(value):
            value = json.loads(value)
        else:
            value = {}
        return value
