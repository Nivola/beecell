# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2020-2022 Regione Piemonte
# (C) Copyright 2018-2026 CSI-Piemonte

from typing import TypedDict, List


class FeBindingDict(TypedDict):
    port: int
    path_cert: str


class FrontendDict(TypedDict):
    name: str
    bind: List[FeBindingDict]


class FeBeDict(TypedDict):
    name: str
    acl_name: str  ## name


class BeServerDict(TypedDict):
    name: str
    ip: str
    port: int


class ReqBeDict(TypedDict):
    name: str
    redirect_https: bool  ### TODO enabled di disabled
    server: List[BeServerDict]


class BeDict(ReqBeDict, total=False):
    cookie: str  # backend.cookie for sticky sessions


FRONTEND_HTTP: FrontendDict = {"name": "www-http", "bind": [{"port": 80}]}

FRONTEND_HTTPS: FrontendDict = {"name": "www-https", "bind": [{"port": 443, "path_cert": "/etc/haproxy/ssl"}]}


class ReqAclFqdnDict(TypedDict):
    name: str  # is_toweb01-lbaas
    fqdn: str  # toweb01.site05.nivolapiemonte.it


class AclFqdnDict(ReqAclFqdnDict, total=False):
    condition: str  # hdr(host)


class CertificateDict(TypedDict):
    name: str
    value: str

class AclFqdn(TypedDict):
    acl: List[AclFqdnDict]

class Backends(TypedDict):
    use: List[FeBeDict]

class HaproxyConfigDict(TypedDict):
    user_pwd: str
    description: str
    nodename: str
    certificate: List[CertificateDict]
    frontend_http: FrontendDict
    frontend_https: FrontendDict
    http_acl_fqdn: AclFqdn
    https_acl_fqdn: AclFqdn
    use_backend_http: Backends
    use_backend_https: Backends
    haproxy_backend: List[BeDict]
