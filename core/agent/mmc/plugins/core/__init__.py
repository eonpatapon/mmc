from twisted.internet import defer
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext, \
                                 xmlrpcCleanup
from mmc.core.version import scmRevision
from mmc.core.subscriptions import SubscriptionManager
from mmc.core.auth import AuthenticationManager
from mmc.core.auth.baseldap import BaseLdapAuthenticator
from mmc.core.auth.externalldap import ExternalLdapAuthenticator
from mmc.core.provisioning import ProvisioningManager
from mmc.core.users import UserManager
from mmc.core.plugins import PluginManager

NOAUTHNEEDED = ['authenticate', 'isCommunityVersion']
VERSION = "3.0.3.2"
APIVERSION = "0:0:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    return True

def activate_2():
    UserManager().register("dummy", DummyUser)

    # Register authenticators
    AuthenticationManager().register("baseldap", BaseLdapAuthenticator)
    AuthenticationManager().register("externalldap", ExternalLdapAuthenticator)

    return True
    
# Plugins
def getEnabledPlugins():
    plugins = []
    for plugin, module in PluginManager().getEnabledPlugins().iteritems():
        plugins.append(plugin)
    return plugins

# Subscriptions
def isCommunityVersion():
    return xmlrpcCleanup(SubscriptionManager().isCommunity())

def getSubscriptionInformation(is_dynamic = False):
    return xmlrpcCleanup(SubscriptionManager().getInformations(is_dynamic))


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

    # Users
    def getUser(self, uid):
        return UserManager().getOne(self.currentContext, uid)

    def getUserAcl(self, uid):        
        return UserManager().getACL(self.currentContext, uid)

    def getUsers(self, search = "*", base = None):
        return UserManager().getAll(self.currentContext, search, base)


class DummyUser:

    def getOne(self, ctx, uid):
        return uid

    def getAll(self, ctx, search, base):
        return 0

    def getACL(self, ctx, uid):
        return ""


class ContextMaker(ContextMakerI):
    """
    Create security context for the base plugin.
    """

    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.user = UserManager().getOne(None, self.userid)
        return s
