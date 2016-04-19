'''
Created on Jan 22, 2014

@author: darkbk
'''
import logging
from functools import wraps
from flask import current_app, request, render_template, abort
from flask_login import current_user

logger = logging.getLogger('gibbon.util.auth')

def login_required(func):
    '''
    If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated before calling the actual view. (If they are
    not, it calls the :attr:`LoginManager.unauthorized` callback.) For
    example::

        @app.route('/post')
        @login_required
        def post():
            pass

    If there are only certain times you need to require that your user is
    logged in, you can do so with::

        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()

    which is essentially the code that this function adds to your views.

    It can be convenient to globally turn off authentication when unit
    testing. To enable this, if either of the application
    configuration variables `LOGIN_DISABLED` or `TESTING` is set to
    `True`, this decorator will be ignored.

    :param func: The view function to decorate.
    :type func: function
    '''
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif current_user is None or not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view

def perms_required(perm):
    """Decorator which specifies that a user must have all the specified roles.
    Example::

        @app.route('/dashboard')
        @roles_required('admin', 'editor')
        def dashboard():
            return 'Dashboard'

    The current user must have both the `admin` role and `editor` role in order
    to view the page.

    :param perm: The required permission. A tupla like (action, object_type)
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            #logger.debug(request.headers['Referer'])
            if current_app.login_manager._login_disabled:
                return fn(*args, **kwargs)
            elif not current_user.is_authenticated():
                abort(401)
                #return current_app.login_manager.unauthorized()
            
            # check if user has the required permission
            can = current_user.filter(perm[0], perm[1])
            can.sort()
            logger.debug("User object permissions for current operation: %s" % can)
            if len(can) > 0:
                return fn(objs=can, *args, **kwargs)
            
            # user doesn't have roles required
            msg = "User %s doesn't have the permissions to access this page." % current_user.email
            logger.error(request.headers['Referer'])
            return render_template('error.html', msg=msg)
            
            #return fn(*args, **kwargs)            
            #logger.debug(current_user)
            """
            perms = [Permission(RoleNeed(role)) for role in roles]
            for perm in perms:
                if not perm.can():
                    return _get_unauthorized_view()
            """
            #return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def can(perm):
    """Decorator used to verify if user can execute an action over a defined
    resource type.
    
    Example::

        @app.route('/dashboard')
        @can('view', 'view.sys.dashboard')
        def dashboard():
            return 'Dashboard'

    :param perm: The required permission. A tupla like (action, resource_type)
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            #logger.debug(request.headers['Referer'])
            if current_app.login_manager._login_disabled:
                return fn(*args, **kwargs)
            elif not current_user.is_authenticated():
                abort(401)
                #return current_app.login_manager.unauthorized()
            
            # check if user has the required permission
            can = current_user.can(perm[0], perm[1], perm[2])
            #logger.debug("User can %s %s: %s" % (perm[0], perm[1], can))
            if can:
                return fn(*args, **kwargs)
            
            # user doesn't have roles required
            msg = "User %s doesn't have sufficient permissions to access this view." % current_user.email
            logger.error(msg)
            return render_template('error.html', title="Authorization error", msg=msg)
        return decorated_view
    return wrapper

def jsonp(func):
    """Wraps JSONified output for JSONP requests.
    
    Took from:  https://gist.github.com/1094140    
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        jsonp = request.args.get('jsonp', False)
        if callback:
            data = str(func(*args, **kwargs))  
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        elif jsonp:
            data = str(func(*args, **kwargs))  
            content = str(jsonp) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)        
        else:
            return func(*args, **kwargs)
    return decorated_function