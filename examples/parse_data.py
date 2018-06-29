from beecell.simple import obscure_data

data = {u'pwd': u'ddhednuhwe', u'name': u'pospso',
        u'other': {u'passwd': u'ddhednuhwe', u'name': u'pospso'},
        u'others': {u'password': u'ddhednuhwe', u'name': u'pospso'}}

print obscure_data(data)
