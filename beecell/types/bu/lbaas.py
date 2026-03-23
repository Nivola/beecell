# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2020-2022 Regione Piemonte
# (C) Copyright 2018-2026 CSI-Piemonte

from typing import TypedDict, List, Union
import ipaddress
from flasgger import fields, Schema
from marshmallow.validate import OneOf, ValidationError




def validate_network(cidrblk: str):
    if cidrblk is None:
        return

    try:
        ipaddress.ip_network(cidrblk)
    except ValueError as ex:
        raise ValidationError(str(ex)) from ex


PROTOCOLS = ["https", "http"]


#
# LB Configuration
#
class LbBackendSchema(Schema):
    name = fields.String(required=True, metadata={"description": "backend name", "example": "test"})
    ip = fields.String(required=True, metadata={"description": "backend ip", "example": "test"}, validate=validate_network)
    port = fields.Integer(required=True, metadata={"description": "backend port", "example": 80})
    protocol = fields.String(
        required=True,
        metadata={
            "example": "http",
            "description": "backend protocol"
        },
        validate=OneOf(PROTOCOLS, error="Protocol must be https or http"),
    )


class LbBackendDict(TypedDict):
    name: str
    ip: str
    port: str
    protocol: str


class LbConfigurationSchema(Schema):
    alias = fields.String(required=True, metadata={"description": "Configuration name", "example": "test"})
    fqdn = fields.String(required=True, metadata={"description": "backend ip", "example": "www.example.csi.it"})
    port = fields.Integer(required=True, metadata={"description": "backend port", "example": 80})
    # ssl_termination = fields.Boolean(required=False, load_default=False, metadata={"description": "When protocolo is https terminate ssl"} )
    protocol = fields.String(
        required=True,
        metadata={
            "example": "http",
            "description": "backend protocol"  # <--- Spostato qui dentro
        },
        validate=OneOf(PROTOCOLS, error="Protocol can only https, http"),
    )
    certificate = fields.String(
        required=False, metadata={"description": "Certificate required only if protocol is https ss_terminate is True"}
    )
    stickySessions = fields.Bool(
        required=False, load_default=False, metadata={"description": "If True use cookies for sticky sessions"}
    )
    redirectHttp = fields.Bool(
        required=False, load_default=False, metadata={"description": "If True redirect http request to https"}
    )
    backends = fields.Nested(LbBackendSchema, many=True, required=True, allow_none=True)
    whiteList = fields.List(
        fields.String(validate=validate_network, metadata={"description": "ip or cidr"}), required=False, allow_none=True
    )


class LbConfigurationDict(TypedDict):
    alias: str
    fqdn: str
    port: str
    ssl_termination: bool
    protocol: str
    certificate: str
    stickySessions: bool
    redirectHttp: bool
    backends: List[LbBackendDict]
    whiteList: List[str]


#
# TAag and Tagset
#
class TagSchema(Schema):
    key = fields.String(required=False, allow_none=False, metadata={"description": "tag key"})
    value = fields.String(required=False, allow_none=False, metadata={"description": "tag value"})


class TagDict(TypedDict):
    key: str
    value: str


class TagSetSchema(Schema):
    tag = fields.Nested(TagSchema, many=False, required=False, allow_none=False)


class TagSetDict(TypedDict):
    tag: List[TagDict]


#
# Security Group
#
class VpcSecurityGroupSchema(Schema):
    security_group_id = fields.List(fields.String(), required=True, metadata={"description": "security group id"})


class VpcSecurityGroupDict(TypedDict):
    security_group_id: List[str]


class LbaasSchema(Schema):
    """schema Marshmallow

    Args:
        Schema (_type_): _description_
    """

    account_id = fields.String(
        required=True,
        metadata={"example": "", "description": "Account id or uuid associated to compute zone"},
    )
    flavour = fields.String(
        required=True,
        metadata={"example": "lb.internet.medium", "description": "service definition of the Lbaas flavour"},
    )
    template = fields.String(
        required=True,
        metadata={"example": "lb.internet.medium", "description": "service definition of the Lbaas instance"},
    )
    instance_identifier = fields.String(required=True, metadata={"description": "The LB instance identifier", "example": ""})
    subnet = fields.String(
        required=False,
        allow_none=True,
        metadata={"example": "", "description": "a vpc subnet in wich the LB will lie"},
    )
    user_password = fields.String(
        required=False,
        allow_none=True,
        metadata={"example": "", "description": "Password for access the lb statistic "},
    )
    # tags = fields.Nested(TagSchema, many=True, required=False, allow_none=True)
    security_group_id = fields.String(required=True, metadata={"description": "security group id"})
    lbaasconfig = fields.Nested(LbConfigurationSchema, many=True, required=False, allow_none=True)


class UpdateLbaasSchema(Schema):
    """Update Lbbaas schema Marshmallow

    Args:
        Schema (_type_): _description_
    """

    user_password = fields.String(
        required=False,
        allow_none=True,
        metadata={"example": "", "description": "Password for access the lb statistic "},
    )
    # tags = fields.Nested(TagSchema, many=True, required=False, allow_none=True)
    lbaasconfig = fields.Nested(LbConfigurationSchema, many=True, required=False, allow_none=True)


class LbaasDict(TypedDict):
    """struttura del dizionari di parametri"""

    account_id: str  # Account id or uuid associated to compute zone
    flavour: str  # service definition of the Lbaas flavour
    template: str  # service definition of the Lbaas instance
    instance_identifier: str  # The LB instance identifier
    subnet: str  # a vpc subnet in wich the LB will lie
    user_password: str  # Password for access the lb statistic
    # tags : List[TagDict]
    security_group_ids: str  # a LB security groups to associate with LB instance
    lbaasconfig: List[LbConfigurationDict]  # Load Balancer configurations


class UpdateLbaasDict(TypedDict):
    """struttura del dizionari di parametri"""

    user_password: str  # Password for access the lb statistic
    # tags : List[TagDict]
    lbaasconfig: List[LbConfigurationDict]  # Load Balancer configurations


class LbaasFalvourDict(TypedDict):
    container: str
    flavor: str
    image: str
    key_name: Union[dict, str]
    #   SiteTorino01: opstkcsi-podto1
    #   SiteTorino02: opstkcsi-podto2
    #   SiteVercelli01: opstkcsi-podvc


class CustomizationDict(TypedDict):
    customization: str
    orchestrator_tag: str
    playbook: str


class LbaasTemplateDict(TypedDict):
    """struttura dei dizionari  presi dalla  service definition per tipologia lbaas"""

    steps_order: dict[str, List[str]]
    customizations: dict[str, CustomizationDict]
    host_group: str
    hypervisor: str
    image: str
    key_name: str
    metrics_prefix: str
    volume_flavor: str


class LbaasConfigDict(LbaasDict, LbaasTemplateDict):
    engine_config: LbaasTemplateDict  # Lbaas implementation template
    computeZone: str
