from beecell.db.manager import RedisManager
from beecell.auth import  IdentityMgr , identity_mgr_factory

if __name__ == "__main__":
    uuid = "2a33d817-c215-4702-9c8e-ab88b22432e8"
    manager = RedisManager(
        "redis://:t5vo5ChFCCe8I1toguvOFXFUW1jU9WSJr4H13aNiOAV@dev-node06.tstsddc.csi.it:30185/0",
        timeout=5,
        max_connections=200,
    )
    idm = identity_mgr_factory(uuid, redismanager=manager)
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52//*//*", "Organization.Division.Account.CATEGORY.AccountServiceDefinition"))
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52//*", "Organization.Division.Account.ServiceTag"))
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52//*", "Organization.Division.Account.ServiceLink"))
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52//*//*", "Organization.Division.Account.ServiceInstance.ServiceLinkInst"))
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52//*//*", "Organization.Division.Account.ServiceInstance.ServiceInstanceConfig"))
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52//*", "Organization.Division.Account.ServiceInstance"))
    print( idm.can( '*',"service","502edae4ab//e0735b8bea//2848529d52", "Organization.Division.Account"))
    print(idm.can("use", "ssh", "pippo", "SshGroup"))
    print(idm.can("use", "service", "pippo", "Organization"))
    print(idm.can("use", "service", "pippo", "Organization"))
    print(idm.can("view", "service", "pippo", "Organization"))
    print(idm.can("*", "service", "pippo", "Organization"))
    print(idm.can("*", "service", "*", "Organization"))
    print(idm.can("*", "service", "*//*", "Organization.Division"))
