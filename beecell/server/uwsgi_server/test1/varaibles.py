# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from gibbon.util.uwsgi_wrapper import uwsgi_util

timeout = 0.5
serverLogFileName = 'log/test1-portal2.log'

info_period = 1
info_status = 'false'

uwsgi_util.cache_set('info_status', info_status)