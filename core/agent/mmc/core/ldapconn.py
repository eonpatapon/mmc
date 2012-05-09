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

log = logging.getLogger()

class LdapConnection(ldapom.LdapConnection):

    def __init__(self, uri, base, login, password, certfile = None):
        ldapom.LdapConnection.__init__(self, uri, base, login, password, certfile)
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
            log.debug("Creating OU %s" % oudn)
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
        for ou in self.search(filter="ou=%s" % name, base=base,
                              scope=ldap.SCOPE_SUBTREE):
            return ou
        return None

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
            log.info("Hook " + hookName + " called.")
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
        subschemasubentry_dn, schema = ldap.schema.urlfetch(self._uri)
        schemaAttrObj = schema.get_obj(ldap.schema.ObjectClass, schemaName)
        if not schemaAttrObj is None:
            return (Set(schemaAttrObj.must) | Set(schemaAttrObj.may))
        else:
            return Set()


class LdapConfigConnection(ldapom.LdapConnection):

    def __init__(self, type, uri, login, password, certfile = None):
        # The LDAP server type
        self.type = type
        # Get LDAP connection configuration
        self._default_base = "cn=config"
        self._schema_base = "cn=schema,cn=config"
        if self.type == "389DS":
            self._schema_base = "cn=schema"
        if uri.startswith("ldapi://"):
            import ldap.sasl
            sasl = ("", ldap.sasl.external())
        else:
            sasl = None
        ldapom.LdapConnection.__init__(self, uri, base = self._default_base, 
                                       login = login, password = password, 
                                       certfile = certfile, sasl = sasl)

    def changeBase(self, base):
        """
        Change the LDAP base of this connexion
        """
        self._base = base

    def hasObjectClass(self, objectClass):
        self.changeBase(self._schema_base)
        if self.type == "OpenLDAP":
            attr = "olcObjectClasses"
        if self.type == "389DS":
            attr = "objectClasses"
        for schema in self.search("(objectClass=*)", [attr]):
            for objCls in schema.__getattr__(attr):
                if "NAME '%s'" % objectClass in objCls:
                    return True
        return False

    # Not supported by OL 2.4
    #def removeSchema(self, cn):
    #    schema = self.getSchema(cn)
    #    schema.delete()

    def addSchema(self, schema_path, schema):
        self.changeBase(self._schema_base)
        schema = os.path.join(schema_path, '%s.ldif.%s' % (schema, self.type))
        os.stat(schema)
        class Parser(LDIFParser):
            def __init__(self, ldif, conn):
                LDIFParser.__init__(self, ldif)
                self._conn = conn        
            def handle(self, dn, entry):
                if self._conn.type == "OpenLDAP":
                    schema = self._conn.new_ldap_node(dn)
                if self._conn.type == "389DS":
                    schema = self._conn.retrieve_ldap_node(self._conn._base)
                for attr, value in entry.iteritems():
                    schema.__setattr__(attr, value)
                schema.save()
        p = Parser(open(schema, 'rb'), self)
        p.parse()


class LdapConnectionError(Exception):
    pass

class DNAlreadyExists(LdapConnectionError):
    pass

class DNDoesNotExists(LdapConnectionError):
    pass

class LdapConfigConnectionError(Exception):
    pass
