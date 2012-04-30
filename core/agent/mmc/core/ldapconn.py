# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import logging
import ldap
import xmlrpclib
import tempfile
from sets import Set
from ldif import LDIFParser
from mmc.support import mmctools, ldapom
from mmc.support.config import PluginConfig, PluginConfigFactory

logger = logging.getLogger()

class LdapConnection(ldapom.LdapConnection):

    def __init__(self, base = None):
        # Get LDAP connection configuration
        self.ldap_config = PluginConfigFactory.new(LdapConfig, "ldap")
        if not base: base = self.ldap_config.base
        ldapom.LdapConnection.__init__(self, self.ldap_config.uri,
            base = base, login = self.ldap_config.login, 
            password = self.ldap_config.password)

        self._default_base = base;

    def changeBase(self, base):
        """
        Change the LDAP base of this connexion
        """
        self._base = base

    def addOU(self, name, base = None):
        """
        Add an organizationalUnit
        """

        if not base: base = self._base

        if not self.check_if_dn_exists(base):
            raise DNDoesNotExists()

        oudn = 'ou=%s,%s' % (name, base)
        if not self.check_if_dn_exists(oudn):
            logger.debug("Creating OU %s" % oudn)
            ou = self.new_ldap_node(oudn)
            ou.objectClass = ['organizationalUnit', 'top']
            ou.ou = name
            ou.save()
            return ou
        else:
            raise DNAlreadyExists()
    
    def getOU(self, name, base = None):
        """
        Returns one organizationalUnit below the base
        """

        if not base: base = self._base
        for ou in self.search(filter="ou=%s" % name,
                              base=base, scope=ldap.SCOPE_ONELEVEL):
            return ou

    def getOUs(self, base = None):
        """
        Returns all organizationalUnits one level below the base
        """

        if not base: base = self._base
        return self.search(filter="objectClass=organizationalUnit",
                           base=base, scope=ldap.SCOPE_ONELEVEL)

    def getOUsTree(self, tree = {}):
        """
        Return a tree of organizationalUnits LdapNodes organized in a
        dictionnary

        {<LdapNode: ou=Test>: {<LdapNode: ou=Test1>: {}}}
        """

        if tree:
            for ou, child in tree.items():
                for child_ou in self.getOUs(ou._dn):
                    tree[ou][child_ou] = {}
                    self.getOUsTree(tree[ou])
            return tree
        else:
            for ou in self.getOUs():
                tree[ou] = {}
            return self.getOUsTree(tree)

    def runHook(self, hookName, uid = None, password = None):
        """
        Run a hook
        """
        if hookName in self.config.hooks:
            logger.info("Hook " + hookName + " called.")
            if uid:
                # Make a temporary ldif file with user entry if an uid is specified
                fd, tmpname = tempfile.mkstemp()
                try:
                    fob = os.fdopen(fd, "wb")
                    user = self.search("uid=%s" % uid)
                    if password:
                        if isinstance(password, xmlrpclib.Binary):
                            password = str(password)
                        # Put user password in clear text in ldif
                        user.userPassword = password
                    user.write_ldif(fob)
                    fob.close()
                    mmctools.shlaunch(self.config.hooks[hookName] + " " + tmpname)
                finally:
                    os.remove(tmpname)
            else:
                mmctools.shlaunch(self.config.hooks[hookName])
    
    def getSchema(self, schemaName):
        """
        Return schema corresponding schemaName

        @param schemaName: schema name
            ex: person, posixAccount
        @type schemaName: str

        @return: schema parameters
        @type list

        For more info on return type, reference to ldap.schema
        """
        subschemasubentry_dn, schema = ldap.schema.urlfetch(self.config.ldapurl)
        schemaAttrObj = schema.get_obj(ldap.schema.ObjectClass,schemaName)
        if not schemaAttrObj is None:
            return (Set(schemaAttrObj.must) | Set(schemaAttrObj.may))
        else:
            return Set()


class LdapConfigConnection(ldapom.LdapConnection):

    def __init__(self):
        # Get LDAP connection configuration
        self.ldap_config = PluginConfigFactory.new(LdapConfig, "ldap")
        self._default_base = "cn=config";
        import ldap.sasl
        ldapom.LdapConnection.__init__(self, "ldapi:///",
            base = self._default_base, login = "", password = "",
            certfile = None, sasl = ("", ldap.sasl.external()))

    def getSchema(self, cn):
        for schema in self.search("(cn=*%s)" % cn, base = "cn=schema,cn=config"):
            return schema
        raise SchemaDoesNotExist()

    # Not supported by OL 2.4
    #def removeSchema(self, cn):
    #    schema = self.getSchema(cn)
    #    schema.delete()

    def addSchema(self, ldif):
        os.stat(ldif)
        class Parser(LDIFParser):
            def __init__(self, ldif, conn):
                LDIFParser.__init__(self, ldif)
                self._conn = conn
            def handle(self, dn, entry):
                schema = self._conn.new_ldap_node(dn)
                for attr, value in entry.iteritems():
                    schema.__setattr__(attr, value)
                schema.save()
        p = Parser(open(ldif, 'rb'), self)
        p.parse()


class LdapConfig(PluginConfig):
    """
    Define values needed by the LDAPConnection class.
    """
    
    uri = 'ldap://127.0.0.1:389'
    base = 'dc=mandriva,dc=com'
    login = 'cn=admin,dc=mandriva,dc=com'
    password = 'secret'
    certfile = ''

    def readConf(self):
        """
        Read LDAP configuration from plugins/ldap.ini
        """

        # Get LDAP server we are connected to
        try:
            self.uri = self.get("main", "uri")
        except:
            pass
        try:
            self.base = self.getdn("main", "base")
        except ldap.LDAPError:
            logger.error("Wrong base DN syntax !")
            logger.error("Will use the default : %s" % self.base)
        except:
            pass
        try:
            self.login = self.getdn("main", "login")
        except ldap.LDAPError:
            logger.error("Wrong login DN syntax !")
            logger.error("Will use the default : %s" % self.login)
        except:
            pass
        try:
            self.password = self.get("main", "password")
        except:
            pass
        try:
            self.certfile = self.get("main", "certfile")
        except:
            pass



class LdapConnectionError(Exception):
    pass

class DNAlreadyExists(LdapConnectionError):
    pass

class DNDoesNotExists(LdapConnectionError):
    pass

class LdapConfigConnectionError(Exception):
    pass

class SchemaDoesNotExist(LdapConfigConnectionError):
    pass
