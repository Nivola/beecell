# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2022 CSI-Piemonte

import logging
from flask import render_template as flask_render_template
from flask_login import current_user

logger = logging.getLogger(__name__)


def _inner_render(url, *argc, **argv):
    """ """
    try:
        res = flask_render_template(url, *argc, **argv)
    except Exception as ex:
        logger.warning('Template %s error' % url, exc_info=True)
        res = ''
    
    return res 


def render_template(url, *argc, **argv):
    """ """
    ver = None
    try:
        ver = current_user.get_portal_version()
        # find the last . in template string
        urllist = url.split('.')
        urllist.insert(-1, ver)
        url_profile = '.'.join(urllist)
        res = flask_render_template(url_profile, *argc, **argv)
        logger.debug('Use template %s version %s' % (url, ver))
        return res
    except Exception as ex:
        logger.warning('Template %s version %s not found. Use default' % (url, ver))
        return flask_render_template(url, *argc, **argv)
