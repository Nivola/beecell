# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

from docutils import nodes
from docutils.parsers.rst import directives, Directive


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


class ApiNode(nodes.Element):
    def __init__(self, *args, **kwargs):
        super(ApiNode, self).__init__(*args, **kwargs)
        self['method'] = ''
        self['uri'] = ''
        self['desc'] = ''


def depart_apinode_latex(self, node):
    pass


def visit_apinode_html(self, node):
    user = 'fa-unlock-alt fa text-success'
    sync = 'fa-flash fa text-info'
    title = ''
    if node['auth'] == 'true':
        user = 'fa-user-secret fa text-danger'
    if node['sync'] == 'false':
        sync = 'fa-gears fa text-success'
    if node['title'] is not None:
        title = "<b>%s</b><br>" % node['title']
    html = ['<div class="col-1"><i class="label label-success">%s</i></div>' % node['method'],
            '<div class="col-5"><i class="%s"></i>&nbsp;' % (user), 
            '<i class="%s"></i>&nbsp;' % (sync),
            '<i class="link">%s</i></div>' % (node['uri']),
            '<div class="col-5">%s%s</div>' % (title, node['desc']),
            '<div class="col-1"><button type="button" name="details" id="%s" class="btn btn-info">'
            'Detail</button></div>' % node['targetid'],
            ]

    self.body.append('\n'.join(html))
    pass


def depart_apinode_html(self, node):
    pass


def visit_grid_detail(self, node):
    pass


def depart_grid_detail(self, node):
    pass


class ExpandDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'method': directives.unchanged,
        'auth': directives.unchanged,
        'sync': directives.unchanged,      
        'uri': directives.unchanged,
        'desc': directives.unchanged,
        'title': directives.unchanged,
    }

    def run(self):
        env = self.state.document.settings.env
        targetid = env.new_serialno('api')
        
        node = nodes.container(rawsource='', ids=["api-%d" % targetid], classes=['row'])
        detail = nodes.container(rawsource='', ids=["details-%d" % targetid], classes=['col-12', 'hide', 'detail'])
        apinode = ApiNode()
        node.append(apinode)
        node.append(detail)
        
        apinode['method'] = self.options.get('method')
        apinode['auth'] = self.options.get('auth')
        apinode['uri'] = html_escape(self.options.get('uri'))
        apinode['desc'] = html_escape(self.options.get('desc'))
        apinode['targetid'] = targetid
        try:
            apinode['title'] = self.options.get('title')
        except:
            apinode['title'] = None        
        try:
            apinode['sync'] = self.options.get('sync')
        except:
            apinode['sync'] = 'true'
        
        self.state.nested_parse(self.content, self.content_offset, detail)        
        return [node]


def setup(app):
    app.add_directive("expand", ExpandDirective)
    app.add_node(ApiNode, html=(visit_apinode_html, depart_apinode_html))
