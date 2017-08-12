from flex.core import load, validate_api_call, validate

class ApiValidator():
    def __init__(self, schema, uri, method):
        self.data = None
        self.code = None
        self.master_schema = schema
        self.schema = None
        self.uri = uri
        self.method = method
        self.keys = []
        self.schema_keys = []
        self.code = None
        
        self.get_schema()
        
    def get_keys(self, data, parent=None):
        for key,value in data.items():
            if parent is not None:
                self.keys.append(u'%s.%s' % (parent, key))
            else:
                self.keys.append(u'%s' % (key))
            
            if isinstance(value, dict):
                self.get_keys(value, key)
            if isinstance(value, list):
                self.get_keys(value[0], key)                
        return self.keys
    
    def parse_data(self):
        self.get_keys(self.data)
        return self.keys    
    
    def get_schema_keys(self, data, parent=None):
        if u'$ref' in data:
            # #/responses/NotFound
            data = data[u'$ref']
            section, ref = data[2:].split(u'/')
            data = self.master_schema[section][ref]            
            self.get_schema_keys(data, parent)
        elif u'schema' in data: 
            data = data[u'schema']
            self.get_schema_keys(data, parent)
        elif u'items' in data: 
            data = data[u'items']
            self.get_schema_keys(data, parent)
        elif u'properties' in data: 
            data = data[u'properties']
            for key,value in data.items():
                if parent is not None:
                    self.schema_keys.append(u'%s.%s' % (parent, key))
                else:
                    self.schema_keys.append(u'%s' % (key))
                
                if value[u'type'] == u'object':
                    self.get_schema_keys(value, key)
                elif value[u'type'] == u'array':
                    self.get_schema_keys(value, key)                    
    
    def parse_schema(self):
        self.get_schema_keys(self.schema[self.code])
        return self.schema_keys
    
    def get_schema(self):
        if self.uri in self.master_schema[u'paths']:
            self.base_schema = self.master_schema[u'paths'][self.uri][self.method]
            self.req_schema = self.base_schema[u'parameters']
            self.schema = self.base_schema[u'responses']
        else:
            raise Exception(u'Swager schema for %s is not defined' % self.uri)
    
    def compare(self):
        s = set(self.parse_schema())
        t = set(self.parse_data())
        res = s.symmetric_difference(t)
        if len(res) > 0:
            raise Exception(u'Schema and data does not superimpose for'\
                            u' keys: %s' % u', '.join(res))

    def validate(self, response):
        validate_api_call(self.master_schema, raw_request=response.request, raw_response=response)
        self.code = str(response.status_code)
        self.data = response.json()
        #self.check_status()
        self.compare()
        return True