# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte

try:
    from urlparse import urlsplit
except ImportError:
    from urllib.parse import urlsplit
from flask import request
from flask_wtf import Form as BaseForm
from wtforms import ValidationError
from beecell.auth import AuthError
from .bootstrap.wtforms_fields import TextField, PasswordField, SelectField
from .bootstrap.wtforms_fields import SubmitField, HiddenField, BooleanField
from .bootstrap.wtforms_widget import TextInput, PasswordInput


class LoginForm(BaseForm):
    """The default login form"""

    email = TextField(label="Username", default="", widget=TextInput())
    password = PasswordField(label="Password", default="", widget=PasswordInput())
    domain = SelectField(label="Domain")
    remember = BooleanField(label="Remember me")
    submit = SubmitField(label="Sign in")
    next = HiddenField()

    def __init__(self, datastore, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.remember.default = False
        self.datastore = datastore

    def validate_next(self, field):
        if field.data:
            url_next = urlsplit(field.data)
            url_base = urlsplit(request.host_url)
            if url_next.netloc and url_next.netloc != url_base.netloc:
                field.data = ""
                raise ValidationError("Invalid url for redirect")

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        if self.email.data.strip() == "":
            self.email.errors.append("Username is not provided")
            return False

        if self.password.data.strip() == "":
            self.password.errors.append("Password is not provided")
            return False

        try:
            self.user = self.datastore.login_user(
                self.email.data,
                self.password.data,
                self.domain.data,
                request.environ["REMOTE_ADDR"],
            )
            res = True
        except AuthError as ex:
            # 0 - Wrong user
            if ex.code == 0:
                self.email.errors.append("User is invalid")
                res = False
            # 1 - Wrong user or password
            elif ex.code == 1:
                self.password.errors.append("Password is invalid")
                res = False
            # 2 - User is disabled
            elif ex.code == 2:
                self.password.errors.append("Account is disabled")
                res = False
            # 3 - Password is expired
            elif ex.code == 3:
                self.password.errors.append("Password is expired")
                res = False
            # 5 - Domain is wrong
            elif ex.code == 5:
                self.domain.errors.append(ex.desc)
                res = False
            #  - Not defined
            else:
                self.password.errors.append(ex.desc)
                res = False

        return res
