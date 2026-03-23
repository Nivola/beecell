# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2020-2022 Regione Piemonte
# (C) Copyright 2018-2026 CSI-Piemonte
#################################

from __future__ import annotations
from curses import meta

# from marshmallow import validates_schema, ValidationError
from marshmallow.validate import OneOf
from flasgger import fields, Schema
from typing import TYPE_CHECKING, TypedDict


class CreatePaasParamRequestSchema(Schema):
    desc = fields.String(required=True, metadata={"description": "The resource description", "example": "test"})
    orchestrator_tag = fields.String(
        required=False,
        load_default="default",
        metadata={
            "description": "orchestrator tag. Use to select a subset of orchestrators where security group must be created.",
        },
    )
    name = fields.String(required=True, metadata={"description": "The security group name", "example": "test"})
    container = fields.String(required=True, metadata={"description": "Container id, uuid or name", "example": "10"})
    tags = fields.String(
        required=False,
        metadata={
            "example": "tag1,tag2",
            "description": "comma separated list of tags to assign",
        },
        allow_none=True,
    )
    compute_zone = fields.String(
        required=True, metadata={"description": "parent compute zone id or uuid", "example": "1"}
    )
    availability_zone = fields.String(
        required=True,
        metadata={"example": "2995", "description": "id, uuid or name of the site where create paas"},
    )
    multi_avz = fields.Boolean(
        load_default=True,
        required=False,
        metadata={
            "example": False,
            "description": "Define if instance must be deployed to work in all the availability zones",
        },
    )
    flavor = fields.String(required=True, metadata={"description": "id, uuid or name of the flavor", "example": "2995"})
    volume_flavor = fields.String(
        required=False,
        metadata={
            "example": "vol.default",
            "description": "volume flavour",
        },
        load_default="compact",
    )
    image = fields.String(required=False, metadata={"description": "id, uuid or name of the image", "example": "2995"})
    vpc = fields.String(required=True, metadata={"description": "id, uuid or name of the vpc", "example": "2995"})
    subnet = fields.String(required=True, metadata={"description": "subnet definition", "example": "10.102.167.90/24"})
    security_group = fields.String(
        required=True,
        metadata={"example": "2995", "description": "id, uuid or name of the security group"},
    )
    engine_admin_user = fields.String(
        required=False,
        allow_none=True,
        metadata={"example": "", "description": "The engine admin user"},
    )
    engine_admin_password = fields.String(
        required=False,
        allow_none=True,
        metadata={"example": "", "description": "The engine admin password"},
    )
    key_name = fields.String(
        required=False,
        metadata={
            "example": "",
            "description": "Openstack public key name",
        },
        allow_none=True,
    )

    version = fields.String(required=False, metadata={"description": "engine version", "example": "5.7"})

    engine = fields.String(
        required=False,
        validate=OneOf(["lbaas"]),
        metadata={"example": "lbaas", "description": "Database engine"},
    )

    engine_configs = fields.Dict(
        required=False,
        allow_none=True,
        metadata={"description": "engine parameters"},
    )
    root_disk_size = fields.Integer(
        required=False, metadata={"description": "Size of root disk", "example": 40}, load_default=40
    )
    resolve = fields.Boolean(
        load_default=True,
        required=False,
        metadata={
            "example": False,
            "description": "Define if stack instances must registered on the availability_zone dns zone",
        },
    )
    hostname = fields.String(
        required=False,
        allow_none=True,
        metadata={ "description": "for compatibility only may be unused"},
    )
    host_group = fields.String(
        required=False,
        allow_none=True,
        metadata={"example": "default", "description": "define the optional host group the db instance belongs to"},
    )
    hypervisor = fields.String(
        required=False, metadata={"description": "type of the hypervisor", "example": "openstack"}
    )
    csi_custom = fields.Boolean(
        required=False,
        metadata={"example": False, "description": "flag to enable post-installation CSI setup"},
        load_default=False,
        allow_none=True,
    )

    enable_monitor = fields.Boolean(required=False, load_default=True, metadata={"description": "Enable monitoring"})


class CreatePaasParamRequestDict(TypedDict):
    desc: str
    orchestrator_tag: str
    name: str
    container: str
    tags: str
    compute_zone: str
    availability_zone: str
    multi_avz: bool
    flavor: str
    volume_flavor: str
    image: str
    vpc: str
    subnet: str
    security_group: str
    engine_admin_user: str
    engine_admin_password: str
    key_name: str
    version: str
    engine: str
    engine_configs: dict
    root_disk_size: int
    resolve: bool
    hostname: str
    host_group: str
    hypervisor: str
    csi_custom: bool
    enable_monitor: bool


class UpdatePaasParamRequestSchema(Schema):
    action = fields.String(required=False, metadata={"description": "acction name", "example": "applay"})
    engine_configs = fields.Dict(
        required=False,
        metadata={
            "description": "engine parameters",
        },
        allow_none=True,
    )


class UpdatePaasParamRequestDict(TypedDict):
    action: str
    engine_configs: dict


class GetPaasEngineResponseSchema(Schema):
    engine = fields.String(required=True, metadata={"description": "Engine name", "example": "lbaas"})
    version = fields.String(required=True, metadata={"description": "Engine version", "example": "5.7"})


class GetPaasEngineResponseDict(TypedDict):
    engine: str
    version: str
