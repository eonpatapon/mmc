import xmlrpclib
from mmc.core.auth import AuthenticatorI, AuthenticationToken, AUTH_CONFIG
from mmc.core.ldapconn import LdapConnection

class BaseLdapAuthenticator(AuthenticatorI):

    def __init__(self, conffile = AUTH_CONFIG, name = "baseldap"):
        AuthenticatorI.__init__(self, conffile, name)

    def authenticate(self, uid, password):
        conn = LdapConnection()
        if not uid == "root":
            users = list(conn.search("uid=%s" % uid))
            if len(users) == 1:
                user = users[0]
            else:
                return AuthenticationToken()
        else:
            user = conn.get_ldap_node(conn.ldap_config.login)
        
        # If the passwd has been encoded in the XML-RPC stream, decode it
        if isinstance(password, xmlrpclib.Binary):
            password = str(password)

        if user.check_password(password):
            return AuthenticationToken(True, uid, password, user)
        else:
            return AuthenticationToken()

    def validate(self):
        return True
