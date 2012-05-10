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
    UserManager().register("Dummy user backend", DummyUser, None)
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

    # Backend
    def canUserHaveGroups(self):
        return xmlrpcCleanup(UserManager().canHaveGroups(self.currentContext))

    # Users
    def canAddUser(self):
        return xmlrpcCleanup(UserManager().canAddUser(self.currentContext))

    def canChangeUserPassword(self, uid):
        return xmlrpcCleanup(UserManager().canChangeUserPassword(self.currentContext, 
                                                                 uid))

    def canChangeUserAttributes(self, uid):
        return xmlrpcCleanup(UserManager().canChangeUserAttributes(self.currentContext, 
                                                                   uid))

    def canRemoveUser(self, uid):
        return xmlrpcCleanup(UserManager().canRemoveUser(self.currentContext, 
                                                         uid))

    def canManageUserBases(self):
        return xmlrpcCleanup(UserManager().canManageUserBases(self.currentContext))

    def getUser(self, uid):
        return xmlrpcCleanup(UserManager().getUser(self.currentContext, uid))

    def getUserAcl(self, uid):        
        return xmlrpcCleanup(UserManager().getUserACL(self.currentContext, uid))

    def getUsers(self, search = "*", base = None):
        return xmlrpcCleanup(UserManager().getUsers(self.currentContext, 
                                                    search, base))

    def addUserBase(self, name, base = None):
        return xmlrpcCleanup(UserManager().addUserBase(self.currentContext, 
                                                       name, base))
    
    def removeUserBase(self, name, recursive = False):
        return xmlrpcCleanup(UserManager().removeUserBase(self.currentContext, 
                                                          name, recursive))

    def addUser(self, uid, password, properties = {}, base = None):
        return xmlrpcCleanup(UserManager().addUser(self.currentContext, uid, 
                                                   password, properties, base))

    def changeUserPassword(self, uid, password, old_password = None, bind = False):
        return xmlrpcCleanup(UserManager().changeUserPassword(self.currentContext, 
                                                              uid, password,
                                                              old_password, bind))

    def changeUserAttributes(self, uid, attrs, log = True):
        return xmlrpcCleanup(UserManager().changeUserAttributes(self.currentContext, 
                                                                uid, attrs, log))

    def removeUser(self, uid):
        return xmlrpcCleanup(UserManager().removeUser(self.currentContext, uid))

    def canAddGroup(self):
        return xmlrpcCleanup(UserManager().canAddGroup(self.currentContext))

    def canEditGroup(self, name):
        return xmlrpcCleanup(UserManager().canEditGroup(self.currentContext, 
                                                        name))

    def canRemoveGroup(self, name):
        return xmlrpcCleanup(UserManager().canRemoveGroup(self.currentContext,
                                                          name))

    def getGroup(self, name):
        return xmlrpcCleanup(UserManager().getGroup(self.currentContext,
                                                    name))

    def getGroups(self, search = "*", base = None):
        return xmlrpcCleanup(UserManager().getGroups(self.currentContext,
                                                     search, base))

    def addGroup(self, name, attrs = {}, base = None):
        return xmlrpcCleanup(UserManager().addGroup(self.currentContext,
                                                    name, attrs, base))

    def changeGroupAttributes(self, name, attrs, log = True):
        return xmlrpcCleanup(UserManager().changeGroupAttributes(self.currentContext,
                                                                 name, attrs, log))

    def addGroupUser(self, name, uid):
        return xmlrpcCleanup(UserManager().addGroupUser(self.currentContext,
                                                        name, uid))

    def removeGroupUser(self, name, uid):
        return xmlrpcCleanup(UserManager().removeGroupUser(self.currentContext,
                                                           name, uid))

    def removeGroupUserFromAll(self, uid):
        return xmlrpcCleanup(UserManager().removeGroupUserFromAll(self.currentContext,
                                                                  uid))

    def removeGroup(self, name):
        return xmlrpcCleanup(UserManager().removeGroup(self.currentContext,
                                                       name))


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
        s.user = UserManager().getUser(None, self.userid)
        return s
