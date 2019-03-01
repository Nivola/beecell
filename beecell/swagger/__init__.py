# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from flex.core import validate_api_call
from logging import getLogger
from apispec import APISpec
from marshmallow.validate import OneOf
from copy import deepcopy

logger = getLogger(__name__)


class SwaggerHelper(object):
    def __init__(self):
        self.spec = APISpec(title=u'', version=u'', plugins=[u'apispec.ext.flask', u'apispec.ext.marshmallow'])

    @staticmethod
    def responses(orig, data):
        new = deepcopy(orig)
        new.update(data)
        return new

    def get_parameters(self, schema):
        """Get swagger query parameters from schema
        
        :param schema: marshmallow schema
        :param where: can be path or query
        """
        fields = schema.__dict__.get(u'_declared_fields', [])
        res = []
        kvargs = {}
        for field, value in fields.items():
            if value.load_from is not None:
                field = value.load_from
            
            context = value.metadata.get(u'context', None)
            if context is not None:
                if context == u'body':
                    kvargs = {
                        u'in': u'body',
                        u'name': u'body',
                        u'schema': {u'$ref': u'#/definitions/%s' % value.nested.__name__}
                    }
                else:
                    kvargs = {
                        u'in': context,
                        u'name': field,
                        u'required': value.required,
                        u'description': value.metadata.get(u'description', u''),
                    }                    
                      
                    field_type = value.__class__.__name__.lower()
                    # logger.warn(value)
                    # logger.warn(field_type)
                    if field_type == u'date':
                        kvargs[u'type'] = u'string'
                        kvargs[u'format'] = u'date'
                    elif field_type == u'datetime':
                        kvargs[u'type'] = u'string'
                        kvargs[u'format'] = u'datetime'
                    elif field_type == u'list':
                        try:
                            kvargs[u'type'] = u'array'
                            kvargs[u'collectionFormat'] = value.metadata.get(u'collection_format', u'')
                            subfield_type = value.container.__class__.__name__.lower()
                            kvargs[u'items'] = {u'type': subfield_type}
                            kvargs[u'name'] = kvargs[u'name'].replace(u'_N', u'.N')
                        except:
                            logger.warn(u'', exc_info=1)
                    else:
                        kvargs[u'type'] = field_type
                    if bool(value.default) is not False:
                        kvargs[u'default'] = value.default
                    if value.validate is not None and isinstance(value.validate, OneOf):
                        kvargs[u'enum'] = value.validate.choices
        
            res.append(kvargs)
        return res


class ApiValidator():
    def __init__(self, schema, uri, method):
        self.logger = getLogger(self.__class__.__module__+ u'.' + self.__class__.__name__)
        
        self.data = None
        self.code = None
        self.master_schema = schema
        self.schema = None
        self.uri = uri
        self.method = method
        self.keys = []
        self.removed_keys= []
        self.schema_keys = {}
        self.code = None
        
        self.get_schema()
        
    def get_keys(self, s, data, parent=None, required=None):
        if isinstance(data, dict):
            for key,value in data.items():
                if required is None or key in required:
                    if parent is not None:
                        key = u'%s.%s' % (parent, key)
                    else:
                        key = key
                    
                    self.keys.append(key)
                    if isinstance(value, dict):
                        self.get_keys(s, value, key, s[key][1])
                    if isinstance(value, list):
                        if len(value) > 0:
                            self.get_keys(s, value[0], key, s[key][1][0]) 
                        elif len(value) == 0:
                            if s[key][1][1]==True and s[key][0] == u'array':
                                self.logger.debug(u'this is not valid key:%s' %key)
                                self.removed_keys.append(key)
                            
        return self.keys
        
    def parse_data(self, s):
        if s != {}:
            self.get_keys(s, self.data)
            self.logger.debug(u'Get all response keys: %s' % self.keys)
            return self.keys
        return []
    
    def get_schema_keys(self, data, parent=None, required=[]):
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
            required = data.get(u'required', [])
            data = data[u'properties']
            for key,value in data.items():
                if key in required:
                    next_required = value.get(u'required', [])
                    if value[u'type'] == u'array':
                        next_required = [value.get(u'items').get(u'required', []), value.get(u'x-nullable')] 
                        allow_empty = value.get(u'x-nullable')
                    
                    if parent is not None:
                        self.schema_keys[u'%s.%s' % (parent, key)] = \
                            [str(value[u'type']), next_required]
                        key = u'%s.%s' % (parent, key)
                    else:
                        self.schema_keys[u'%s' % (key)] = \
                            [str(value[u'type']), next_required]
                    
                    if value[u'type'] == u'object':
                        self.get_schema_keys(value, key)
                    elif value[u'type'] == u'array':
                        self.get_schema_keys(value, key)                    
                    
    def parse_schema(self):
        self.get_schema_keys(self.schema[self.code])
        self.logger.debug(u'Get all schema keys: %s' % self.schema_keys)   
        return self.schema_keys
    
    def get_schema(self):
        if self.uri in self.master_schema[u'paths']:
            self.base_schema = self.master_schema[u'paths'][self.uri][self.method][u'parameters']
            self.schema = self.base_schema[u'responses']
        else:
            raise Exception(u'Swager schema for %s is not defined' % self.uri)
    
    def compare(self):
        s = self.parse_schema()
        t = set(self.parse_data(s))
        s = set(s.keys())  
        
        # inspect keys nullable in a subtree
        key = set()
        for k in s:
            for r in self.removed_keys: 
                if k.startswith(u'%s.' % r):
                    key.add(k)
        
        res = s.symmetric_difference(t).symmetric_difference(key)
        if len(res) > 0:
            self.logger.error(u'Schema and data does not superimpose for keys: %s' % u', '.join(res))
            raise Exception(u'Schema and data does not superimpose for keys: %s' % u', '.join(res))
        self.logger.debug(u'Schema and response keys are the same')

    def validate(self, response):
        validate_api_call(self.master_schema, raw_request=response.request, raw_response=response)
        self.code = str(response.status_code)
        if response.content != u'':
            self.data = response.json()
            self.compare()
            self.logger.debug(u'Api request %s is valid' % self.uri)
        return True
