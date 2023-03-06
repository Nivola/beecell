# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from datetime import datetime
from six import ensure_text


def parse_date(data_str, format=None):
    """Parse string to date

    :param data_str: date in string format
    :param format: format date ex: %Y-%m-%dT%H:%M
    :return: date
    """
    if format is None:
        time_format = "%Y-%m-%dT%H:%M:%SZ"
    else:
        time_format = format

    res = None
    if data_str is not None:
        res = datetime.strptime(data_str, time_format)
    return res


def format_date(date, format=None, microsec=False):
    """Format date as rfc3339.

    Ref. https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html

    :param date: datetime object
    :param format: format date ex: %Y-%m-%dT%H:%M
    :return: formatted date
    """

    if format is None:
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        if microsec is True:
            time_format += ".%f"
    else:
        time_format = format
    res = None
    if date is not None:
        res = ensure_text(date.strftime(time_format))
    return res


def get_date_from_timestamp(date):
    if date is not None:
        return datetime.fromtimestamp(date)
    else:
        return None


def get_timestamp_from_date(date):
    if date is not None:
        return datetime.timestamp(date)
    else:
        return None
