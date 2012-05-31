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

    def authenticate(self, user, password):
        """
        Authenticate an user with her/his password against the active 
        authentication backend.

        Return a Deferred resulting to true if the user has been successfully
        authenticated, else false.
        """
        d = defer.maybeDeferred(AuthenticationManager().authenticate, user, password, self.session)
        d.addCallback(ProvisioningManager().doProvisioning)
        d.addCallback(self._cbAuthenticate)
        return d

    def _cbAuthenticate(self, token):
        """
        Callback for authentication.
        """
        ret = token.isAuthenticated()
        if ret:
            user = UserManager().getUser(self.currentContext, token.login)
            record = AF().log(PLUGIN_NAME, AA.CORE_AUTH_USER, [(str(user), AT.USER)])
            record.commit()
        return ret

    # Backend
    def getUserManagerName(self):
        return xmlrpcCleanup(UserManager().getManagerName())

    def canUserHaveGroups(self):
        return xmlrpcCleanup(UserManager().canHaveGroups())

    def getUserExtensionsList(self):
        return xmlrpcCleanup(UserManager().getUserExtensionsList())

    def getGroupExtensionsList(self):
        return xmlrpcCleanup(UserManager().getGroupExtensionsList())

    # Users
    def canAddUser(self):
        return xmlrpcCleanup(UserManager().canAddUser(self.currentContext))

    def canEditUser(self, user):
        return xmlrpcCleanup(UserManager().canEditUser(self.currentContext, 
                                                       user))

    def canRemoveUser(self, user):
        return xmlrpcCleanup(UserManager().canRemoveUser(self.currentContext, 
                                                         user))
    
    def canChangeUserPassword(self, user):
        return xmlrpcCleanup(UserManager().canChangeUserPassword(self.currentContext, 
                                                                 user))

    def canManageUserBases(self):
        return xmlrpcCleanup(UserManager().canManageUserBases(self.currentContext))

    def getUser(self, user):
        return xmlrpcCleanup(UserManager().getUser(self.currentContext, user))

    def getUserAcl(self, user):        
        return xmlrpcCleanup(UserManager().getUserACL(self.currentContext, user))

    def getUserGroups(self, user):
        return xmlrpcCleanup(UserManager().getUserGroups(self.currentContext, 
                                                         user))

    def getUsers(self, search = "*", start = None, end = None, base = None):
        return xmlrpcCleanup(UserManager().getUsers(self.currentContext, 
                                                    search, start, end, base))

    def addUserBase(self, name, base = None):
        return xmlrpcCleanup(UserManager().addUserBase(self.currentContext, 
                                                       name, base))
    
    def removeUserBase(self, name, recursive = False):
        return xmlrpcCleanup(UserManager().removeUserBase(self.currentContext, 
                                                          name, recursive))

    def addUser(self, user, password, properties = {}, base = None):
        return xmlrpcCleanup(UserManager().addUser(self.currentContext, user, 
                                                   password, properties, base))

    def changeUserPassword(self, user, password, old_password = None, bind = False):
        return xmlrpcCleanup(UserManager().changeUserPassword(self.currentContext, 
                                                              user, password,
                                                              old_password, bind))

    def changeUserProperties(self, user, props, log = True):
        return xmlrpcCleanup(UserManager().changeUserProperties(self.currentContext, 
                                                                user, props, log))

    def removeUser(self, user):
        return xmlrpcCleanup(UserManager().removeUser(self.currentContext, user))

    def canAddGroup(self):
        return xmlrpcCleanup(UserManager().canAddGroup(self.currentContext))

    def canEditGroup(self, group):
        return xmlrpcCleanup(UserManager().canEditGroup(self.currentContext, 
                                                        group))

    def canRemoveGroup(self, group):
        return xmlrpcCleanup(UserManager().canRemoveGroup(self.currentContext,
                                                          group))

    def getGroup(self, group):
        return xmlrpcCleanup(UserManager().getGroup(self.currentContext,
                                                    group))

    def getGroups(self, search = "*", start = None, end = None, base = None):
        return xmlrpcCleanup(UserManager().getGroups(self.currentContext,
                                                     search, start, end, base))

    def addGroup(self, group, props = {}, base = None):
        return xmlrpcCleanup(UserManager().addGroup(self.currentContext,
                                                    group, props, base))

    def changeGroupProperties(self, group, props, log = True):
        return xmlrpcCleanup(UserManager().changeGroupProperties(self.currentContext,
                                                                 group, props, log))

    def addGroupUser(self, group, user):
        return xmlrpcCleanup(UserManager().addGroupUser(self.currentContext,
                                                        group, user))

    def removeGroupUser(self, group, user):
        return xmlrpcCleanup(UserManager().removeGroupUser(self.currentContext,
                                                           group, user))

    def removeGroupUserFromAll(self, user):
        return xmlrpcCleanup(UserManager().removeGroupUserFromAll(self.currentContext,
                                                                  user))

    def removeGroup(self, group):
        return xmlrpcCleanup(UserManager().removeGroup(self.currentContext,
                                                       group))

    # User extensions

    def addUserExtension(self, name, user, password, props = {}):
        return xmlrpcCleanup(UserManager().addUserExtension(self.currentContext,
                                                            name, user, 
                                                            password, props))

    def changeUserExtensionProps(self, name, user, props, log = True):
        return xmlrpcCleanup(UserManager().changeUserExtensionProps(self.currentContext,
                                                    name, user, props, log))

    def removeUserExtension(self, name, user):
        return xmlrpcCleanup(UserManager().removeUserExtension(self.currentContext,
                                                    name, user))

    # Group extensions
    
    def addGroupExtension(self, name, group, props = {}):
        return xmlrpcCleanup(UserManager().addGroupExtension(self.currentContext,
                                                    name, group, props))

    def changeGroupExtensionProps(self, name, group, props, log = True):
        return xmlrpcCleanup(UserManager().changeGroupExtensionProps(self.currentContext,
                                                    name, group, props, log))

    def removeGroupExtension(self, name, group):
        return xmlrpcCleanup(UserManager().removeGroupExtension(self.currentContext,
                                                    name, group))


class DummyUser:
    """
    A user backend that does nothing
    """

    def getOne(self, ctx, user):
        return user

    def getACL(self, ctx, user):
        return ""

    def getAll(self, ctx, search = "*", start = None, end = None, base = None):
        return []


class ContextMaker(ContextMakerI):
    """
    Create security context for the core plugin.
    """

    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.user = UserManager().getUser(None, self.userid)
        return s
