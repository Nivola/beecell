import binascii
import zlib
import json
import pickle
from beecell.db.manager import RedisManager
from .base import AuthError

# from beecell.db.manager import RedisManager
# from beecell.auth.base import AuthError

from typing import List, Union

PREFIX = "identity:"
PREFIX_INDEX = "identity:index:"


class IdentityMgr(object):
    """
    identity manager
    this class manage  the operation on identity as stored on redis
    the identity is created using the user permission in filed user.perms
    When the user restirct his current permissions the full list of permission are stred in field  fullperms

    """

    def __init__(self) -> None:
        self._expire = None
        self._uuid: str = None
        self._mgr: RedisManager = None
        self._key_value: str = None
        self._identity: dict = None
        self._compressed_perms: str = None
        self._fullcompressed_perms: str = None
        self._modified: bool = False
        self._perms: List[List] = None
        self._fullperms: List[List] = None
        pass

    @property
    def expire(self) -> int:
        return self._expire if type(self._expire) == int else 3600

    @expire.setter
    def expire(self, value):
        self._expire = value

    def _store(self, never_expire=False):
        """Set beehive identity

        :param never_expire: if True identity key never expires
        """
        self._key_value = pickle.dumps(self._identity)
        user = self._identity.get("user", {}).get("id")
        self._mgr.conn.setex(PREFIX + self._uuid, self.expire, self._key_value)
        if never_expire:
            self._mgr.conn.persist(PREFIX + self._uuid)
        # add identity to identity user index
        self._mgr.conn.lpush(PREFIX_INDEX + user, self._uuid)
        # set index expire time
        self._mgr.conn.expire(PREFIX_INDEX + user, self.expire)

    def _remove(self):
        """Remove beehive identity with token uid"""
        try:
            user = self.user
            self._mgr.conn.delete(PREFIX + self._uuid)

            # delete identity from identity user index
            self._mgr.conn.lrem(PREFIX_INDEX + user, 1, self._uuid)

        except Exception as ex:
            raise AuthError(exdesc="", code=10)

    def _get(self, update_ttl: bool = True):
        """Get identity from redis

        :raises AuthError: raise :class:`AuthError`
        """
        try:
            self._key_value = self._mgr.conn.get(PREFIX + self._uuid)
            if self._key_value is not None:
                self._identity = pickle.loads(self._key_value)
                if "fullperms" not in self._identity:
                    self._identity["fullperms"] = self._identity.get("user", {}).get("perms")
                self._compressed_perms = self._identity.get("user", {}).get("perms")
                self._fullcompressed_perms = self._identity["fullperms"]
            if update_ttl:
                self.reset_ttl()
            else:
                raise AuthError("Identity %s does not exist or is expired" % self._uuid, desc="", code=1)
        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    def reset_ttl(self):
        """reset  identity ttl

        :raises AuthError: raise :class:`AuthError`
        """
        try:
            self._mgr.conn.expire(PREFIX + self._uuid, self.expire)
            self._mgr.conn.expire(PREFIX_INDEX + self.user, self.expire)
        # set index expire time

        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    def save(self):
        """
        Save identity if not modified only reset ttl
        """
        if self._modified:
            self._store()
        else:
            self.reset_ttl()

    @property
    def ttl(self) -> int:
        """
        Get identity ttl
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            return self._mgr.conn.ttl(PREFIX + self._uuid)
        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    @property
    def identity(self) -> dict:
        """
        Get identity dictionary

        :raises AuthError: raise :class:`AuthError`
        """
        try:
            if self._identity is None:
                self._get()
            return self._identity
        except Exception as ex:
            raise AuthError(ex)

    @property
    def user(self) -> str:
        """
        Get identity dictionary
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            if self._identity is None:
                self._get()
            return self._identity.get("user", {}).get("id")
        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    @property
    def full_perms(self) -> List[List]:
        """
        Get identity full list of permissions

        :returns perms List[List]
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            if self._fullperms is None:
                self._fullperms = json.loads(zlib.decompress(binascii.a2b_base64(self._fullcompressed_perms)))
            return self._fullperms

        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    @property
    def perms(self) -> List[List]:
        """
        Get identity list of permissions

        :returns perms List[List]
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            if self._perms is None:
                self._perms = json.loads(zlib.decompress(binascii.a2b_base64(self._compressed_perms)))
            return self._perms
        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    @perms.setter
    def perms(self, newperms: List[List]):
        """
        Get identity list of permissions

        :param newperms perms List[List[int, int, str, str, str, int, str]]
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            self._perms = newperms
            self._compressed_perms = binascii.b2a_base64(zlib.compress(json.dumps(self._perms).encode("utf-8")))
            self._identity["user"]["perms"] = self._compressed_perms
            self._key_value = pickle.dumps(self._identity)
            self._modified = True

        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    def restore_full_perms(self):
        self._identity["user"]["perms"] = self._fullcompressed_perms
        self._compressed_perms = self._fullcompressed_perms
        self._perms = json.loads(zlib.decompress(binascii.a2b_base64(self._compressed_perms)))
        self._modified = True

    def can(self, action: str = None, objtype: str = None, objid: str = None, objdef: str = None):
        """
        Verify if identity can execute an action over a certain object type.
        |0-pid  |1-oid |2-type     |3-definition                         | 4-objid       | 5-aid|6-action
        |985    |124   |'service'  |'ServiceType.ServiceDefinition'      |'*//*'         |1     |'*'    |
        |1009   |127   |'service'  |'ServiceType.ServiceProcess'         |'*//*'         |1     |'*'    |
        |969    |122   |'service'  |'ServiceType'                        |'*'            |1     |'*'    |
        |1017   |128   |'service'  |'ServiceCatalog'                     |'*'            |1     |'*'    |
        |1025   |129   |'service'  |'ServiceJob'                         |'*'            |1     |'*'    |
        |1041   |131   |'service'  |'ServicePriceList.ServicePriceMetric'|'*//*'         |1     |'*'    |
        |1033   |130   |'service'  |'ServicePriceList'                   |'*'            |1     |'*'    |
        |1073   |135   |'ssh'      |'SshGroup.SshNode.SshUser'           |'*//*//*'      |1     |'*'    |
        |1065   |134   |'ssh'      |'SshGroup.SshNode'                   |'*//*'         |1     |'*'    |
        |1057   |133   |'ssh'      |'SshGroup'                           |'*'            |1     |'*'    |
        |1081   |136   |'ssh'      |'SshKey'                             |'*'            |1     |'*'    |
        |1089   |137   |'ssh'      |'SshLogin'                           |'*'            |1     |'*'    |
        |3554372|444299|'resource' |'Zabbix.Host'                        |'*//*'         |1     |'*'    |
        |3554396|444302|'resource' |'Zabbix.Hostgroup'                   |'*//*'         |1     |'*'    |
        |3554420|444305|'resource' |'Zabbix.Template'                    |'*//*'         |1     |'*'    |
        |3554348|444296|'container'|'Zabbix'                             |'*'            |1     |'*'    |
        |1871913|233990|'ssh'      |'SshKey'                             |'8d83c41bdd'   |2     |'view' |
        |1870769|233847|'ssh'      |'SshGroup'                           |'5312d5694c'   |2     |'view' |
        |1870777|233848|'ssh'      |'SshGroup.SshNode'                   |'5312d5694c//*'|2     |'view' |
        |1870776|233848|'ssh'      |'SshGroup.SshNode'                   |'5312d5694c//*'|6     |'use'  |

        :param action: str es * view use write,
        :param objtype: str service, ssh, resource ,
        :param objid: str, structured object id
        :param objdef: str object definition :

        :return: bool
        :raises AuthError: raise :class:`AuthError`
        """
        action = action.lower()
        objtype = objtype.lower()
        objid = objid.lower()
        objdef = objdef.lower()
        objids = objid.split("//")
        try:
            res = {}
            for perm in self.full_perms:
                perm_objtype = perm[2].lower()
                perm_objdef = perm[3].lower()
                perm_objid = perm[4].lower()
                perm_action = perm[6].lower()

                if objtype == perm_objtype:
                    if objdef == perm_objdef:
                        if perm_action == "*" or perm_action == action:
                            perm_objids = perm_objid.split("//")
                            if len(objids) == len(perm_objids):
                                for i in range(0, len(perm_objids)):
                                    if perm_objids[i] == "*" or perm_objids[i] == objids[i]:
                                        return True
            return False
        except Exception as ex:
            raise AuthError(ex, desc="", code=10)

    def set_perms(self, newperms: List[List], store: bool = True):
        """
        check if identity has permissions for new perms
        if identity new perms are copatible with perms then new perms are set ti identity
        """
        for check_per in newperms:
            check_objtype = check_per[2]
            check_objdef = check_per[3]
            check_objid = check_per[4]
            check_action = check_per[6]
            if not self.can(action=check_action, objtype=check_objtype, objid=check_objid, objdef=check_objdef):
                raise AuthError(
                    "action %s, on %s %s %s cannot be perfomed by user"
                    % (check_action, check_objtype, check_objdef, check_objid),
                    desc="",
                    code=1,
                )
        self.perms = newperms
        if store:
            self._store()


def identity_mgr_factory(uuid: str, controller=None, module=None, apimanager=None, redismanager=None) -> IdentityMgr:
    """
    IdentityMgr factory
    """
    try:
        ret = IdentityMgr()
        ret._uuid = uuid
        if redismanager is not None:
            ret._mgr = redismanager
        elif apimanager is not None:
            ret.expire = apimanager.expire
            ret._mgr = apimanager.redis_identity_manager
        elif module is not None:
            ret.expire = module.api_manager.expire
            ret._mgr = module.api_manager.redis_identity_manager
        elif controller is not None:
            ret._mgr = controller.module.api_manager.redis_identity_manager
            ret.expire = controller.module.api_manager.expire
        else:
            raise AuthError("cannot find a redis connection", desc="", code=10)
        ret._get()
        return ret
    except Exception as ex:
        raise AuthError(ex, desc="", code=10)
