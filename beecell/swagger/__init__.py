# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

from logging import getLogger
#from copy import deepcopy
from typing import TYPE_CHECKING, Dict, Type
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flasgger import Schema
from marshmallow import missing
from marshmallow.schema import SchemaMeta
from marshmallow.validate import OneOf
#from flex.core import validate_api_call
if TYPE_CHECKING:
    from marshmallow.fields import Field as SchemaField
logger = getLogger(__name__)
#global_marshmallow_plugin = MarshmallowPlugin()  # imported by some views

VALID_CONTEXTS = {"query", "path", "header", "body"}

class SwaggerHelper(object):
    def __init__(self):
        #global global_marshmallow_plugin
        self.spec = APISpec(
            title="",
            version="",
            plugins=[FlaskPlugin(), MarshmallowPlugin()],
            openapi_version="2.0",
        )

    #@staticmethod
    #def responses(orig, data):
    #    new = deepcopy(orig)
    #    new.update(data)
    #    return new

    def get_parameters(self, schema: Type[Schema]):
        """Get swagger query parameters from schema and convert them
        to Swagger/OpenAPI parameter definitions

        :param schema: marshmallow schema
        :param where: can be path or query

        example:

            class MySchema(Schema):
                name = fields.String(required=True, metadata={"context": "query"})

        becomes:

            {
                "in": "query",
                "name": "name",
                "required": true,
                "type": "string"
            }
        """
        try:
            from apispec.ext.marshmallow.field_converter import FieldConverterMixin
            field_converter = FieldConverterMixin()
        except:
            field_converter = None

        if not isinstance(schema, (Schema, SchemaMeta)):
            raise TypeError(
                f"Expected schema to be a Marshmallow Schema or Schema class, got {type(schema)}"
            )

        # get declared marshmallow fields
        fields: Dict[str, 'SchemaField'] = schema.__dict__.get("_declared_fields", {})
        res = []
        for field_name, value in fields.items():
            kvargs = {}
            # does the field have an alias that is used instead?
            if getattr(value, "data_key", None) is not None:
                field_name = value.data_key

            # does the field specify a context? (e.g. body, query)
            context = value.metadata.get("context", None)
            if context is not None:
                if context not in VALID_CONTEXTS:
                    raise ValueError(
                        f"Invalid context '{context}' for field '{field_name}'. "
                        f"Valid contexts: {VALID_CONTEXTS}"
                    )

                if context == "body":
                    if not hasattr(value, "nested") or value.nested is None:
                        raise ValueError(
                            f"Field '{field_name}' marked as body must have a 'nested' schema"
                        )
                    # nested schena representing the request body
                    kvargs = {
                        "in": "body",
                        "name": "body",
                        "schema": {"$ref": f"#/definitions/{value.nested.__name__}"},
                    }
                else:
                    kvargs = {
                        "in": context,
                        "name": field_name,
                        "required": value.required,
                        "description": value.metadata.get("description", ""),
                    }

                    # map marshmallow field class to swagger type

                    # TODO replace everything with the proper functions
                    field_type = value.__class__.__name__.lower()

                    if field_converter is not None:
                        # returns a dict with type and format
                        kvargs.update(field_converter.field2type_and_format(value))
                    else:
                        if field_type == "date":
                            kvargs["type"] = "string"
                            kvargs["format"] = "date"
                        elif field_type == "datetime":
                            kvargs["type"] = "string"
                            kvargs["format"] = "datetime"
                        #elif field_type == "list" # handled in common code below
                        else:
                            kvargs["type"] = field_type

                    if field_type == "list":
                        #kvargs["type"] = "array"
                        kvargs["collectionFormat"] = value.metadata.get("collection_format", "multi")
                        if hasattr(value, "inner") and value.inner is not None:
                            subfield_type = value.inner.__class__.__name__.lower()
                            kvargs["items"] = {"type": subfield_type}
                        else:
                            raise ValueError(
                                f"Field '{field_name}' is a List but 'inner' type is missing"
                            )
                    if getattr(value, "default", missing) is not missing:
                        kvargs["default"] = value.default
                    if value.validate is not None and isinstance(value.validate, OneOf):
                        kvargs["enum"] = value.validate.choices
            else:
                logger.warning(
                    "Field '%s' in schema '%s' has no context defined. "
                    "It will not appear in Swagger parameters.",
                    field_name,
                    schema.__name__,
                )
            if kvargs:
                res.append(kvargs)
        return res

"""
class ApiValidator(object):
    def __init__(self, schema, uri, method):
        self.logger = getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

        self.data = None
        self.code = None
        self.master_schema = schema
        self.schema = None
        self.uri = uri
        self.method = method
        self.keys = []
        self.removed_keys = []
        self.schema_keys = {}
        self.code = None

        self.get_schema()

    def get_keys(self, s, data, parent=None, required=None):
        if isinstance(data, dict):
            for key, value in data.items():
                if required is None or key in required:
                    if parent is not None:
                        key = "%s.%s" % (parent, key)
                    else:
                        key = str(key)

                    self.keys.append(key)
                    if isinstance(value, dict):
                        self.get_keys(s, value, key, s[key][1])
                    if isinstance(value, list):
                        if len(value) > 0:
                            self.get_keys(s, value[0], key, s[key][1][0])
                        elif len(value) == 0:
                            if s[key][1][1] == True and s[key][0] == "array":
                                self.logger.debug("this is not valid key:%s" % key)
                                self.removed_keys.append(key)

        return self.keys

    def parse_data(self, s):
        if s != {}:
            self.get_keys(s, self.data)
            self.logger.debug("Get all response keys: %s" % self.keys)
            return self.keys
        return []

    def get_schema_keys(self, data, parent=None, required=None):
        if required is None:
            required = []
        if "$ref" in data:
            # #/responses/NotFound
            data = data["$ref"]
            section, ref = data[2:].split("/")
            data = self.master_schema[section][ref]
            self.get_schema_keys(data, parent)
        elif "schema" in data:
            data = data["schema"]
            self.get_schema_keys(data, parent)
        elif "items" in data:
            data = data["items"]
            self.get_schema_keys(data, parent)
        elif "properties" in data:
            required = data.get("required", [])
            data = data["properties"]
            for key, value in data.items():
                if key in required:
                    next_required = value.get("required", [])
                    if value["type"] == "array":
                        next_required = [
                            value.get("items").get("required", []),
                            value.get("x-nullable"),
                        ]
                        allow_empty = value.get("x-nullable")

                    if parent is not None:
                        self.schema_keys["%s.%s" % (parent, key)] = [
                            str(value["type"]),
                            next_required,
                        ]
                        key = "%s.%s" % (parent, key)
                    else:
                        self.schema_keys["%s" % (key)] = [
                            str(value["type"]),
                            next_required,
                        ]

                    if value["type"] == "object":
                        self.get_schema_keys(value, key)
                    elif value["type"] == "array":
                        self.get_schema_keys(value, key)

    def parse_schema(self):
        self.get_schema_keys(self.schema[self.code])
        self.logger.debug("Get all schema keys: %s" % self.schema_keys)
        return self.schema_keys

    def get_schema(self):
        if self.uri in self.master_schema["paths"]:
            self.base_schema = self.master_schema["paths"][self.uri][self.method]["parameters"]
            self.schema = self.base_schema["responses"]
        else:
            raise Exception("Swager schema for %s is not defined" % self.uri)

    def compare(self):
        s = self.parse_schema()
        t = set(self.parse_data(s))
        s = set(s.keys())

        # inspect keys nullable in a subtree
        key = set()
        for k in s:
            for r in self.removed_keys:
                if k.startswith("%s." % r):
                    key.add(k)

        res = s.symmetric_difference(t).symmetric_difference(key)
        if len(res) > 0:
            self.logger.error("Schema and data does not superimpose for keys: %s" % ", ".join(res))
            raise Exception("Schema and data does not superimpose for keys: %s" % ", ".join(res))
        self.logger.debug("Schema and response keys are the same")

    def validate(self, response):
        validate_api_call(self.master_schema, raw_request=response.request, raw_response=response)
        self.code = str(response.status_code)
        if response.content != "":
            self.data = response.json()
            self.compare()
            self.logger.debug("Api request %s is valid" % self.uri)
        return True
"""
