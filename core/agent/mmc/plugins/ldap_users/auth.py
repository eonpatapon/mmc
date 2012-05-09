import os.path
import logging
import xmlrpclib
from mmc.site import mmcconfdir
from mmc.support.config import PluginConfigFactory
from mmc.core.auth import AuthenticatorI, AuthenticationToken
from mmc.core.ldapconn import LdapConnection
from mmc.plugins.ldap_users.config import LdapUsersConfig

log = logging.getLogger()

AUTH_CONFIG = os.path.join(mmcconfdir, "plugins", "ldap_users.ini")

class LdapUsersAuthenticator(AuthenticatorI):

    def __init__(self, conffile = AUTH_CONFIG, name = "ldap"):
        AuthenticatorI.__init__(self, conffile, name)
        self.ldap_config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")

    def authenticate(self, uid, password):
        conn = LdapConnection(self.ldap_config.uri, self.ldap_config.base, 
                              self.ldap_config.login, self.ldap_config.password,
                              self.ldap_config.certfile)
        if not uid == "root":
            users = list(conn.search("uid=%s" % uid))
            if len(users) == 1:
                user = users[0]
            else:
                return AuthenticationToken()
        else:
            user = conn.get_ldap_node(self.ldap_config.login)
        
        # If the passwd has been encoded in the XML-RPC stream, decode it
        if isinstance(password, xmlrpclib.Binary):
            password = str(password)

        if user.check_password(password):
            return AuthenticationToken(True, uid, password, user)
        else:
            return AuthenticationToken()

    def validate(self):
        return True
