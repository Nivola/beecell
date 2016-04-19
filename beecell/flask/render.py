'''
Created on May 23, 2014

@author: darkbk
'''
import logging
from flask import render_template as flask_render_template
from flask_login import current_user

logger = logging.getLogger(__name__)

def render_template(url, *argc, **argv):
    try:
        url_profile = '%s.%s' % (url, current_user.get_profile())
        res = flask_render_template(url_profile, *argc, **argv)
        logger.debug('Use profile template: %s' % url_profile)
        return res
    except Exception as ex:
        logger.debug('Use default template: %s' % url)
        return flask_render_template(url, *argc, **argv)