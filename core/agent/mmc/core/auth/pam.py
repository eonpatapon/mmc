import PAM
from mmc.core.auth import AuthenticatorI, AuthenticationToken, AUTH_CONFIG

class PAMAuthenticator(AuthenticatorI): 

    def __init__(self, conffile = AUTH_CONFIG, name = "pam"):
        AuthenticatorI.__init__(self, conffile, name)

    def authenticate(self, uid, password):

        if not uid or not password:
            return AuthenticationToken()

        auth = PAM.pam()
        auth.start("passwd", uid)
        auth.set_item(PAM.PAM_CONV, lambda auth, query_list, userData: [(password, 0)])
        try:
            auth.authenticate()
        except:
            return AuthenticationToken()
        else:        
            return AuthenticationToken(True, uid, password, uid)

    def validate(self):
        return True
