from __future__ import annotations
import binascii
import zlib
import json
import pickle
from beecell.db.manager import RedisManager
from beecell.debug import dbgprint
from .base import AuthError

# from beecell.db.manager import RedisManager
# from beecell.auth.base import AuthError

from typing import List, Union

PREFIX = "identity:"
PREFIX_INDEX = "identity:index:"
EXPIRE = 3600


class IdentityMgr(object):
    """
    identity manager
    this class manage  the operation on identity as stored on redis
    the identity is created using the user permission in filed user.perms
    When the user restirct his current permissions the full list of permission are stred in field  fullperms

    """

    def __init__(self) -> None:
        self._user: str = None
        self._expire = EXPIRE
        self._uuid: str = None
        self._mgr: RedisManager = None
        self._identity: dict = None
        self._compressed_perms: str = None
        self._fullcompressed_perms: str = None
        self._modified: bool = False
        self._perms: List[List] = None
        self._fullperms: List[List] = None
        pass

    @property
    def ttl(self) -> int:
        return self._mgr.conn.ttl(PREFIX + self._uuid)

    @ttl.setter
    def ttl(self, expire: int) -> int:
        self._mgr.conn.expire(PREFIX + self._uuid, expire)
        self._mgr.conn.expire(PREFIX_INDEX + self.user, expire)

    @property
    def expire(self) -> int:
        return self._expire

    def set_expire(self, value):
        self._expire = value if type(value) == int else EXPIRE

    def _store(self, never_expire=False):
        """Set beehive identity

        :param never_expire: if True identity key never expires
        """
        key_value = pickle.dumps(self._identity)
        user = self._identity.get("user", {}).get("id")
        self._mgr.conn.setex(PREFIX + self._uuid, self._expire, key_value)
        # add identity to identity user index
        self._mgr.conn.lpush(PREFIX_INDEX + user, self._uuid)
        # set index expire time
        if never_expire:
            self._mgr.conn.persist(PREFIX + self._uuid)
            self._mgr.conn.persist(PREFIX_INDEX + user)
        else:
            self._mgr.conn.expire(PREFIX_INDEX + user, self.expire)

    def _remove(self):
        """Remove beehive identity with token uid"""
        try:
            user = self.user
            self._mgr.conn.delete(PREFIX + self._uuid)

            # delete identity from identity user index
            self._mgr.conn.lrem(PREFIX_INDEX + user, 1, self._uuid)

        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex),  desc="", code=AuthError.CONNECTIONERROR)

    def _get(self, update_ttl: bool = True):
        """Get identity from redis

        :raises AuthError: raise :class:`AuthError`
        """
        try:
            key_value = self._mgr.conn.get(PREFIX + self._uuid)
            if key_value is not None:
                self._identity = pickle.loads(key_value)
                if "fullperms" not in self._identity:
                    self._identity["fullperms"] = self._identity.get("user", {}).get("perms")
                self._compressed_perms = self._identity.get("user", {}).get("perms")
                self._fullcompressed_perms = self._identity["fullperms"]

                if update_ttl:
                    self.reset_ttl()
            else:
                raise AuthError(info="Identity %s does not exist or is expired" % self._uuid, desc="", code=AuthError.TOKENEXPIRED)
        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.UNDEFINED)

    def reset_ttl(self, never_expire=False):
        """reset  identity ttl

        :raises AuthError: raise :class:`AuthError`
        """

        ##dbgprint(never_expire=never_expire, uuid=self._uuid)
        try:
            if never_expire:
                self._mgr.conn.persist(PREFIX + self._uuid)
                self._mgr.conn.persist(PREFIX_INDEX + self.user)
            else:
                ttl = self._expire if type(self._expire) == int else EXPIRE
                self._mgr.conn.expire(PREFIX + self._uuid, ttl)
                self._mgr.conn.expire(PREFIX_INDEX + self.user, ttl)
        # set index expire time

        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.CONNECTIONERROR)

    def save(self, never_expire=False):
        """
        Save identity if not modified only reset ttl
        """
        if self._modified:
            self._store(never_expire)
        else:
            self.reset_ttl(never_expire)

    @property
    def ttl(self) -> int:
        """
        Get identity ttl
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            return self._mgr.conn.ttl(PREFIX + self._uuid)
        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.CONNECTIONERROR)

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
        except AuthError as ex:
                raise ex
        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.UNDEFINED)

    @property
    def user(self) -> str:
        """
        Get identity dictionary
        :raises AuthError: raise :class:`AuthError`
        """
        try:
            if self._user is not None:
                return self._user
            if self._identity is None:
                self._get()
            self._user = self._identity.get("user", {}).get("id")
            return self._user

        except AuthError as ex:
            raise ex
        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.UNDEFINED)

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
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.UNDEFINED)

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
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.UNDEFINED)

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
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=AuthError.UNDEFINED)

    def restore_full_perms(self):
        self._identity["user"]["perms"] = self._fullcompressed_perms
        self._compressed_perms = self._fullcompressed_perms
        self._perms = json.loads(zlib.decompress(binascii.a2b_base64(self._compressed_perms)))
        self._modified = True

    def can(self, action: str = None, objtype: str = None, objid: str = None, objdef: str = None):
        """
        Verify if identity can execute an action over a certain object type.
        usate solo 2-type 3-definition 4-objid 6-action
        |0-pid  |1-oid |2-type     |3-definition                         | 4-objid       | 5-aid|6-action
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
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="", code=10)

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
                    info="action %s, on %s %s %s cannot be perfomed by user"
                    % (check_action, check_objtype, check_objdef, check_objid),
                    desc="",
                    code=AuthError.FORBIDDEN,
                )
        self.perms = newperms
        if store:
            self._store()

    @staticmethod
    def set_identity(uuid, identity, redismanager: RedisManager, expire=True, expire_time=None) -> IdentityMgr:
        """Set beehive identity with token uid

        :param uid: authorization token
        :param identity: dictionary with login identity
        :param expire: if True identity key expire after xx seconds
        :param expire_time: [optional] det expire time in seconds
        """

        ##dbgprint(uuid=uuid, identity=identity)
        idmgr = IdentityMgr()
        idmgr._uuid = uuid
        idmgr._expire = expire_time if type(expire_time) == int else EXPIRE
        idmgr._mgr = redismanager

        idmgr._modified = True
        idmgr._identity = identity
        idmgr._compressed_perms = idmgr._identity.get("user", {}).get("perms")
        idmgr._store(never_expire=not expire)
        return idmgr

        # if expire_time is None:
        #     expire_time = self.expire

        # val = pickle.dumps(identity)
        # user = dict_get(identity, "user.id")
        # self.module.redis_identity_manager.conn.setex(self.prefix + uid, expire_time, val)
        # if expire is False:
        #     self.module.redis_identity_manager.conn.persist(self.prefix + uid)

        # # add identity to identity user index
        # self.module.redis_identity_manager.conn.lpush(self.prefix_index + user, uid)
        # # set index expire time
        # self.module.redis_identity_manager.conn.expire(self.prefix_index + user, expire_time)

        # self.logger.info("Set identity %s in redis" % uid)

    @staticmethod
    def get_identity(uuid, redismanager: RedisManager, update_ttl: bool = False) -> dict:
        """Get identity
        if identity does not exixte raise AuthError
        :param uid: identity id
        :param redimanager identity manager
        :return: {'uid':..., 'user':..., timestamp':..., 'pubkey':..., 'seckey':...}
        """
        imgr = IdentityMgr()
        imgr._uuid = uuid
        imgr._mgr = redismanager
        imgr._get(update_ttl=update_ttl)
        data = imgr._identity
        if update_ttl:
            data["ttl"] = imgr._expire
        else:
            data["ttl"] = imgr.ttl


        ##dbgprint(result=data)
        return data

    @staticmethod
    def get_identities(redismanager: RedisManager):
        """Get identities

        :return: [{'uid':..., 'user':..., timestamp':..., 'pubkey':..., 'seckey':...}, ..]
        """
        try:
            res = []
            for key in redismanager.conn.keys(PREFIX + "*"):
                try:
                    identity = redismanager.conn.get(key)
                except Exception as ex:
                    ##dbgprint(ex)
                    continue
                data = pickle.loads(identity)
                data["ttl"] = redismanager.conn.ttl(key)
                res.append(data)
            return res
        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=str(ex), desc="No identities found", code=AuthError.UNDEFINED)

    @staticmethod
    def factory(
        uuid: str, controller=None, module=None, apimanager=None, redismanager: RedisManager = None
    ) -> IdentityMgr:
        """
        IdentityMgr factory
        """
        try:
            ret = IdentityMgr()
            ret._uuid = uuid
            if redismanager is not None:
                ret._mgr = redismanager
            elif apimanager is not None:
                ret.set_expire(apimanager.expire)
                ret._mgr = apimanager.redis_identity_manager
            elif module is not None:
                ret.set_expire(module.api_manager.expire)
                ret._mgr = module.api_manager.redis_identity_manager
            elif controller is not None:
                ret.set_expire(controller.module.api_manager.expire)
                ret._mgr = controller.module.api_manager.redis_identity_manager
            else:
                raise AuthError(info="cannot find a redis connection", desc="", code=AuthError.CONNECTIONERROR)

            ##dbgprint( idmgr=ret),
            ret._get()
            ##dbgprint( idmgr=ret),
            return ret
        except Exception as ex:
            ##dbgprint(ex)
            raise AuthError(info=ex, desc="", code=AuthError.PASSWORDEXPIRED)


def identity_mgr_factory(
    uuid: str, controller=None, module=None, apimanager=None, redismanager: RedisManager = None
) -> IdentityMgr:
    """
    IdentityMgr factory
    """
    return IdentityMgr.factory(
        uuid, controller=controller, module=module, apimanager=apimanager, redismanager=redismanager
    )
