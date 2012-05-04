from twisted.internet import defer
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory as AF
from mmc.core.ldapconn import LdapConnection
from mmc.core.auth import AuthenticationManager
from mmc.core.provisioning import ProvisioningManager

NOAUTHNEEDED = ['authenticate', 'isCommunityVersion']
VERSION = "3.0.3.2"
APIVERSION = "0:0:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    return True

class RpcProxy(RpcProxyI):

    def authenticate(self, uid, password):
        """
        Authenticate an user with her/his password against a LDAP server.
        Return a Deferred resulting to true if the user has been successfully
        authenticated, else false.
        """
        d = defer.maybeDeferred(AuthenticationManager().authenticate, uid, password, self.session)
        d.addCallback(ProvisioningManager().doProvisioning)
        d.addCallback(self._cbAuthenticate)
        return d

    def _cbAuthenticate(self, token):
        """
        Callback for authentication.
        """
        ret = token.isAuthenticated()
        #if ret:
        #    userdn = LdapUserGroupControl().searchUserDN(token.login)
        #    record = AF().log(PLUGIN_NAME, AA.BASE_AUTH_USER, [(userdn, AT.USER)])
        #    record.commit()
        return ret

def getUserAcl(uid):
    return ""
