#!/usr/bin/env python
# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte


from typing import TypedDict, Dict, List, Any


class OutputsDict(TypedDict):
    """parameters for actions while creating, deleting and updating a resource stack  

    Args:
        TypedDict (_type_): _description_
    """
    name: str
    desc: str
    value: str



class ServiceUserDetail(TypedDict, total=False):
    name: str
    pwd: str
    attribs: str
    privs: str

class CustomizationDetail(TypedDict, total=False):
    playbook: str
    customization: str
    orchestrator_tag: str

class CustomizationDict(CustomizationDetail):
    pass
class EngineBlock(TypedDict, total=False):
    port: int
    customization: str
    license: str
    charset: str
    service_users: Dict[str, List[ServiceUserDetail]]
    steps_order: Dict[str, List[str]]
    customizations: Dict[str, CustomizationDetail]

class EngineParams(TypedDict, total=False):
    hypervisor: str
    image: str
    volume_flavor: str
    host_group: str
    lvm: Dict[str, Any]
    mount_point: Dict[str, Any]
    versions: List[str]
    engine: EngineBlock
