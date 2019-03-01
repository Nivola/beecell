# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import datetime
import wtforms_widget as widgets
from wtforms.compat import text_type
from wtforms.fields import core as fields

_unset_value = object()


class StringField(fields.StringField):
    """This field is the base for most of the more complicated fields, and represents an ``<input type="text">``.
    """
    widget = widgets.TextInput()
    
    def __init__(self, label=None, _name=None, widget=None, **kwargs):
        super(StringField, self).__init__(label=label, _name=_name, widget=widget, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(_name.replace('_', ' ').title())


class IntegerField(fields.IntegerField):
    """A text field, except all input is coerced to an integer. Erroneous input is ignored and will not be accepted as
    a value.
    """
    widget = widgets.TextInput()
    
    def __init__(self, label=None, _name=None, widget=None, **kwargs):
        super(IntegerField, self).__init__(label=label, _name=_name, widget=widget, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(_name.replace('_', ' ').title())


class DecimalField(fields.DecimalField):
    """A text field which displays and coerces data of the `decimal.Decimal` type.

    :param places: How many decimal places to quantize the value to for display on form. If None, does not quantize
        value.
    :param rounding: How to round the value during quantize, for example `decimal.ROUND_UP`. If unset, uses the
        rounding value from the current thread's context.
    """
    widget = widgets.TextInput()
    
    def __init__(self, label=None, _name=None, widget=None, **kwargs):
        super(DecimalField, self).__init__(label=label, _name=_name, widget=widget, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(_name.replace('_', ' ').title())


class FloatField(fields.FloatField):
    """A text field, except all input is coerced to an float.  Erroneous input is ignored and will not be accepted as a
    value.
    """
    widget = widgets.TextInput()
    
    def __init__(self, label=None, _name=None, widget=None, **kwargs):
        super(FloatField, self).__init__(label=label, _name=_name, widget=widget, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(_name.replace('_', ' ').title())


class BooleanField(fields.BooleanField):
    """Represents an ``<input type="checkbox">``.

    :param false_values: If provided, a sequence of strings each of which is an exact match string of what is
        considered a "false" value. Defaults to the tuple ``('false', '')``
    """
    widget = widgets.CheckboxInput()
    
    def __init__(self, label=None, _name=None, widget=None, **kwargs):
        super(BooleanField, self).__init__(label=label, _name=_name, widget=widget, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(_name.replace('_', ' ').title())


class DateTimeField(fields.DateTimeField):
    """A text field which stores a `datetime.datetime` matching a format.
    """
    widget = widgets.TextInput()
    
    def __init__(self, label=None, _name=None, widget=None, **kwargs):
        super(DateTimeField, self).__init__(label=label, _name=_name, widget=widget, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(_name.replace('_', ' ').title())


class DateField(DateTimeField):
    """Same as DateTimeField, except stores a `datetime.date`.
    """
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super(DateField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.datetime.strptime(date_str, self.format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))


class TextField(StringField):
    """Legacy alias for StringField
    """
    pass


class TextAreaField(TextField):
    """This field represents an HTML ``<textarea>`` and can be used to take multi-line input.
    """
    widget = widgets.TextArea()


class PasswordField(TextField):
    """A StringField, except renders an ``<input type="password">``.

    Also, whatever value is accepted by this field
    """
    widget = widgets.PasswordInput()


class FileField(TextField):
    """Can render a file-upload field.  Will take any passed filename value, if any is sent by the browser in the post
    params.  This field will NOT actually handle the file upload portion, as wtforms does not deal with individual
    frameworks' file handling capabilities.
    """
    widget = widgets.FileInput()


class HiddenField(TextField):
    """HiddenField is a convenience for a StringField with a HiddenInput widget.

    It will render as an ``<input type="hidden">`` but otherwise coerce to a string.
    """
    widget = widgets.HiddenInput()


class SubmitField(BooleanField):
    """Represents an ``<input type="submit">``. This allows checking if a given submit button has been pressed.
    """
    widget = widgets.SubmitInput()


class SelectField(fields.SelectField):
    """This field is the base for most of the more complicated fields, and represents an ``<input type="text">``.
    """
    widget = widgets.Select()
    
    def __init__(self, label=None, validators=None, coerce=text_type, choices=None, **kwargs):
        super(SelectField, self).__init__(label=label, validators=validators, coerce=coerce, choices=choices, **kwargs)
        # replace original implementation with simple string label
        self.label = label if label is not None else self.gettext(label.replace('_', ' ').title())
