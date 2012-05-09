from twisted.internet import defer
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext, \
                                 xmlrpcCleanup
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory as AF
from mmc.core.subscriptions import SubscriptionManager
from mmc.core.auth import AuthenticationManager
from mmc.core.auth.pam import PAMAuthenticator
from mmc.core.auth.externalldap import ExternalLdapAuthenticator
from mmc.core.provisioning import ProvisioningManager
from mmc.core.users import UserManager
from mmc.core.plugins import PluginManager

from mmc.plugins.core.audit import AA, AT, PLUGIN_NAME

NOAUTHNEEDED = ['authenticate', 'isCommunityVersion']
VERSION = "3.0.3.2"
APIVERSION = "0:0:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    UserManager().register("Dummy user backend", DummyUser)
    UserManager().select("Dummy user backend")

    # Register authenticators
    AuthenticationManager().register("pam", PAMAuthenticator)
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
        Authenticate an user with her/his password against the active 
        authentication backend.

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
        if ret:
            user = UserManager().getOne(None, token.login)
            record = AF().log(PLUGIN_NAME, AA.CORE_AUTH_USER, [(str(user), AT.USER)])
            record.commit()
        return ret

    # Users
    def canAddUser(self):
        return UserManager().canAddOne(self.currentContext)

    def canChangeUserPassword(self, uid):
        return UserManager().canChangePassword(self.currentContext, uid)

    def canChangeUserAttributes(self, uid):
        return UserManager().canChangeAttributes(self.currentContext, uid)

    def canRemoveUser(self, uid):
        return UserManager().canRemoveOne(self.currentContext, uid)

    def canAddUserBase(self):
        return UserManager().canAddBase(self.currentContext)

    def canUserHaveGroups(self):
        return UserManager().canHaveGroups(self.currentContext)

    def getUser(self, uid):
        return UserManager().getOne(self.currentContext, uid)

    def getUserAcl(self, uid):        
        return UserManager().getACL(self.currentContext, uid)

    def getUsers(self, search = "*", base = None):
        return UserManager().getAll(self.currentContext, search, base)

    def addUserBase(self, name, base = None):
        return UserManager().addBase(self.currentContext, name, base)

    def addUser(self, uid, password, properties = {}, base = None):
        return UserManager().addOne(self.currentContext, uid, password, 
                                    properties, base)

    def changeUserPassword(self, uid, password, old_password = None, bind = False):
        return UserManager().changePassword(self.currentContext, uid, password,
                                            old_password, bind)

    def changeUserAttributes(self, uid, attrs, log = True):
        return UserManager().changeAttributes(self.currentContext, uid, attrs,
                                              log)

    def removeUser(self, uid):
        return UserManager().removeOne(self.currentContext, uid)


class DummyUser:
    """
    A user backend that does nothing
    """

    def canAddOne(self, ctx):
        return False

    def canChangePassword(self, ctx):
        return False

    def canChangeAttributes(self, ctx, uid):
        return False

    def canRemoveOne(self, ctx, uid):
        return False

    def canAddBase(self, ctx):
        return False

    def canHaveGroups(self, ctx):
        return False

    def getOne(self, ctx, uid):
        return uid

    def getACL(self, ctx, uid):
        return ""

    def getAll(self, ctx, search, base):
        return 0


class ContextMaker(ContextMakerI):
    """
    Create security context for the core plugin.
    """

    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.user = UserManager().getOne(None, self.userid)
        return s
