# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte

from __future__ import unicode_literals
from cgi import escape
from wtforms.compat import text_type, iteritems

__all__ = (
    "CheckboxInput",
    "FileInput",
    "HiddenInput",
    "ListWidget",
    "PasswordInput",
    "RadioInput",
    "Select",
    "SubmitInput",
    "TableWidget",
    "TextArea",
    "TextInput",
    "Option",
)


def html_params(**kwargs):
    """Generate HTML parameters from inputted keyword arguments.

    The output value is sorted by the passed keys, to provide consistent output
    each time this function is called with the same parameters.  Because of the
    frequent use of the normally reserved keywords `class` and `for`, suffixing
    these with an underscore will allow them to be used.

    >>> html_params(name='text1', id='f', class_='text') == 'class="text" id="f" name="text1"'
    True
    """
    params = []
    for k, v in sorted(iteritems(kwargs)):
        if k in ("class_", "class__", "for_"):
            k = k[:-1]
        if v is True:
            params.append(k)
        else:
            params.append('%s="%s"' % (text_type(k), escape(text_type(v), quote=True)))
    return " ".join(params)


class HTMLString(text_type):
    def __html__(self):
        return self


class ListWidget(object):
    """Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """

    def __init__(self, html_tag="ul", prefix_label=True):
        assert html_tag in ("ol", "ul")
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = ["<%s %s>" % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append("<li>%s %s</li>" % (subfield.label, subfield()))
            else:
                html.append("<li>%s %s</li>" % (subfield(), subfield.label))
        html.append("</%s>" % self.html_tag)
        return HTMLString("".join(html))


class TableWidget(object):
    """Renders a list of fields as a set of table rows with th/td pairs.

    If `with_table_tag` is True, then an enclosing <table> is placed around the
    rows.

    Hidden fields will not be displayed with a row, instead the field will be
    pushed into a subsequent table row to ensure XHTML validity. Hidden fields
    at the end of the field list will appear outside the table.
    """

    def __init__(self, with_table_tag=True):
        self.with_table_tag = with_table_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            kwargs.setdefault("id", field.id)
            html.append("<table %s>" % html_params(**kwargs))
        hidden = ""
        for subfield in field:
            if subfield.type == "HiddenField":
                hidden += text_type(subfield)
            else:
                html.append(
                    "<tr><th>%s</th><td>%s%s</td></tr>" % (text_type(subfield.label), hidden, text_type(subfield))
                )
                hidden = ""
        if self.with_table_tag:
            html.append("</table>")
        if hidden:
            html.append(hidden)
        return HTMLString("".join(html))


class Input(object):
    """Render a basic ``<input>`` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """

    html_params = staticmethod(html_params)

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        if "value" not in kwargs:
            value = field._value()
        else:
            value = kwargs["value"]

        res = [
            '<div class=""><div>',
            '<input type="%s" class="form-control" id="%s" name="%s" value="%s" placeholder="%s">'
            % (self.input_type, field.id, field.id, field.default, field.label),
            "</div></div>",
        ]
        return HTMLString("".join(res))


class TextInput(Input):
    """Render a single-line text input."""

    input_type = "text"


class PasswordInput(Input):
    """Render a password input.

    For security purposes, this field will not reproduce the value on a form
    submit by default. To have the value filled in, set `hide_value` to
    `False`.
    """

    input_type = "password"

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs):
        if self.hide_value:
            kwargs["value"] = ""
        return super(PasswordInput, self).__call__(field, **kwargs)


class HiddenInput(Input):
    """Render a hidden input."""

    input_type = "hidden"

    def __call__(self, field, **kwargs):
        res = [
            '<input type="%s" class="form-control" id="%s" name="%s" value="%s">'
            % (self.input_type, field.id, field.id, field.default)
        ]
        return HTMLString("".join(res))


class CheckboxInput(Input):
    """Render a checkbox.

    The ``checked`` HTML attribute is set if the field's data is a non-false value.
    """

    input_type = "checkbox"

    def __call__(self, field, **kwargs):
        res = [
            '<div class=""><div>',
            '<div class="checkbox">',
            "<label></label>",
            '<input type="checkbox">%s' % (field.label),
            "<label>",
            "</div></div></div>",
        ]
        return HTMLString("".join(res))


class RadioInput(Input):
    """Render a single radio button.

    This widget is most commonly used in conjunction with ListWidget or some
    other listing, as singular radio buttons are not very useful.
    """

    input_type = "radio"

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs["checked"] = True
        return super(RadioInput, self).__call__(field, **kwargs)


class FileInput(object):
    """
    Renders a file input chooser field.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        return HTMLString("<input %s>" % html_params(name=field.name, type="file", **kwargs))


class SubmitInput(Input):
    """Renders a submit button.

    The field's label is used as the text of the submit button instead of the
    data on the field.
    """

    input_type = "submit"

    def __call__(self, field, **kwargs):
        res = [
            '<div class=""><div>',
            '<button type="submit" id="%s" class="btn btn-lg btn-primary btn-block">%s</button>'
            % (field.id, field.label),
            "</div></div>",
        ]
        return HTMLString("".join(res))


class TextArea(object):
    """Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        return HTMLString(
            "<textarea %s>%s</textarea>"
            % (
                html_params(name=field.name, **kwargs),
                escape(text_type(field._value())),
            )
        )


class Select(object):
    """Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True

        html = ['<select class="form-control" id="%s" name="%s">' % (field.id, field.name)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append("</select>")

        return HTMLString("".join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        options = dict(kwargs, value=value)
        if selected:
            options["selected"] = True
        return HTMLString("<option %s>%s</option>" % (html_params(**options), escape(text_type(label))))


class Option(object):
    """Renders the individual option from a select field.

    This is just a convenience for various custom rendering situations, and an
    option by itself does not constitute an entire field.
    """

    def __call__(self, field, **kwargs):
        return Select.render_option(field._value(), field.label, field.checked, **kwargs)
