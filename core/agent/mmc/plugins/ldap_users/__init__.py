# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com/
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

"""
A simple plugin for managing ldap users and groups for the MMC agent.
"""

import ldap
import ldap.dn
import logging
import os.path
from mmc.site import datadir
from mmc.core.version import scmRevision
from mmc.core.ldapconn import LdapConnection, LdapConfigConnection
from mmc.core.audit import AuditFactory as AF
from mmc.core.users import UserManager, UserI, GroupI
from mmc.core.auth import AuthenticationManager
from mmc.support import ldapom
from mmc.support.config import PluginConfigFactory
from mmc.support.mmctools import delete_diacritics
from mmc.plugins.ldap_users.audit import AA, AT, PLUGIN_NAME
from mmc.plugins.ldap_users.config import LdapUsersConfig
from mmc.plugins.ldap_users.auth import LdapUsersAuthenticator

VERSION = "3.0.3.2"
APIVERSION = "0:0:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

logger = logging.getLogger()

def activate():
    config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
    # Check LDAP credentials
    logger.debug("Checking LDAP credentials")
    try:
        Ldap = LdapConnection(config.uri, config.base, config.login,
                              config.password, config.certfile)
    except ldap.INVALID_CREDENTIALS:
        logger.error("Can't bind to LDAP: invalid credentials.")
        return False
    # Check and load necessary schemas in LDAP
    logger.debug("Checking LDAP schemas")
    schemas = os.path.join(datadir, 'doc', 'python-mmc-users', 'contrib')
    try:
        LdapConfig = LdapConfigConnection(config.type, config.config_uri,
                                          config.config_login, config.config_password)
        if not LdapConfig.hasObjectClass('lmcUserObject'):
            LdapConfig.addSchema(schemas, 'mmc')
            logger.info("MMC schema loaded in the LDAP directory.")
        if config.type == "OpenLDAP":
            if not LdapConfig.hasObjectClass('namedObject'):
                LdapConfig.addSchema(schemas, 'rfc2307bis')
                logger.info("rfc2307bis schema loaded in the LDAP directory.")
    except:
        logger.warning("Can't access LDAP cn=config database. Using cn=schema.")
        try:
            schema = Ldap.getSchema("lmcUserObject")
            if len(schema) <= 0:
                logger.error("MMC schema seems not included in the LDAP directory.")
                logger.error("The schema can be found in %s" % schemas)
                return False
            if config.type == "OpenLDAP":
                schema = Ldap.getSchema("namedObject")
                if len(schema) <= 0:
                    logger.error("rfc2307bis schema seems not included in the LDAP directory.")
                    logger.error("The schema can be found in %s" % schemas)
                    return False
        except:
            logger.error("Invalid MMC schema.")
            return False
    logger.debug("LDAP schemas are ok.")
    # Create required OUs
    ous = [ config.users_ou, config.groups_ou ]
    for ou in ous:
        if not Ldap.getOU(ou):
            Ldap.addOU(ou)
    # Create the default group
    groups = LdapGroups()
    try:
        groups.addOne(None, config.default_group)
        logger.info("Default user group %s created." % config.default_group)
    except GroupAlreadyExists:
        pass

    return True

def activate_2():
    config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
    UserManager().register(config.backend_name, LdapUsers, LdapGroups)
    UserManager().select(config.backend_name)

    AuthenticationManager().register("ldap", LdapUsersAuthenticator)

    return True


class LdapUsers(LdapConnection, UserI):

    audit_plugin_name = PLUGIN_NAME
    audit_mod_attr = AA.USERS_MOD_USER_ATTR

    classes = ['top',
               'person',
               'inetOrgPerson',
               'organizationalPerson']
    attrs = ['uid',
             'userPassword',
             'jpegPhoto',
             'sn', # Lastname
             'givenName', # Firstname
             'preferredLanguage',
             'title',
             'mail',
             'telephoneNumber',
             'mobile', # Mobile phone
             'facsimileTelephoneNumber', # Fax
             'homePhone',
             'homePostalAddress']

    def __init__(self):
        self.config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
        LdapConnection.__init__(self, self.config.uri, self.config.base,
                                self.config.login, self.config.password,
                                self.config.certfile)
        # Limit queries to the users OU
        self.changeBase(str(self.getOU(self.config.users_ou)))

    def getOne(self, ctx, uid):
        """
        Get user from the directory
        """
        # If uid is already an LdapNode
        # return it directly
        if isinstance(uid, ldapom.LdapNode):
            return uid
        # Search the user
        for user in self.search('uid=%s' % uid):
            return user
        # Handle the special admin login
        if uid == "root":
            if self.config.type == "OpenLDAP":
                return self.retrieve_ldap_node(self._login)
            if self.config.type == "389DS":
                return self._login
        raise UserDoesNotExists()

    def getACL(self, ctx, uid):
        """
        Get user MMC ACLs from directory
        """
        user = self.getOne(ctx, uid)

        if 'lmcACL' in user:
            return str(user.lmcACL)
        else:
            return ""

    def getAll(self, ctx, search = "*", base = None):
        """
        Return the list of users below the base
        """
        if not base: base = self._base;
        filter = "(|(uid=%s)(givenName=%s)(sn=%s)(telephoneNumber=%s)(mail=%s))" % \
            (search, search, search, search, search)
        return list(self.search(filter, base=base))

    def canManageBases(self, ctx):
        """
        Is the connected user allowed to add/remove user OUs
        """
        return True

    def addBase(self, ctx, name, base = None):
        """
        Add an OU for users
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_ADD_USER_OU, [(name, AT.ORGANIZATIONAL_UNIT)])
        ou = self.addOU(self, name, base)
        r.commit()

        return ou

    def removeBase(self, ctx, name, recursive = False):
        """
        Add an OU for users
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_DEL_USER_OU, [(name, AT.ORGANIZATIONAL_UNIT)])
        ou = self.getOU(name)
        if ou:
            if recursive:
                self.delete_r(str(ou))
            else:
                self.delete(str(ou))
            r.commit()

        return True

    def canAddOne(self, ctx):
        """
        Is the user allowed to add users
        """
        return True

    def addOne(self, ctx, uid, password, attrs = {}, base = None):
        """
        Add inetOrgUser user to base
        """
        if not base: base = self._base;

        r = AF().log(PLUGIN_NAME, AA.USERS_ADD_USER, [(uid, AT.USER)])

        try:
            user = self.getOne(ctx, uid)
            raise UserAlreadyExists()
        except UserDoesNotExists:
            # Create the user
            user = self.new_ldap_node('uid=%s,%s' % (uid, base))
            user.objectClass = self.classes
            # Required fields
            user.cn = uid
            user.uid = uid
            user.sn = uid
            # Fill attributes
            for attr, value in attrs.iteritems():
                if attr in self.attrs:
                    user.__setattr__(attr, value)
            user.save()
            r.commit()
            # Set the password
            self.changePassword(ctx, user, password)
            # Run hooks
            self.runHook("users.adduser", uid, password)

            return user

    def canHaveGroups(self, ctx):
        """
        Can the users have groups
        """
        return True

    def getGroups(self, ctx, uid):
        """
        Get the user's groups
        """
        user = self.getOne(ctx, uid)
        groups = []
        for group in LdapGroups().getAll(ctx):
            if 'uniqueMember' in group and str(user) in group.uniqueMember:
                groups.append(group)

        return groups

    def canChangePassword(self, ctx, uid):
        """
        Is the connected user allowed to change uid password
        """
        return True

    def changePassword(self, ctx, uid, password, old_password = None, bind = False):
        """
        Change the user password using LDAP Password Modify Extended Operation
        """
        user = self.getOne(ctx, uid)
        r = AF().log(PLUGIN_NAME, AA.USERS_MOD_USER_PASSWORD, [(str(user.uid), AT.USER)])

        # Bind as the user to change the password
        if bind:
            conn = ldapom.LdapConnection(self._uri,
                                         base = self._base,
                                         login = str(user),
                                         password = old_password)
            user = conn.get_ldap_node(str(user))

        user.set_password(password)

        r.commit()

        self.runHook("users.changeuserpassword", str(user.uid), password)

        return user

    def canChangeAttributes(self, ctx, uid):
        """
        Is the connected user allowed to change uid attributes
        """
        return True

    def changeAttributes(self, ctx, uid, attrs, log = True):
        """
        Change attributes of a user

        attrs: dict((attr, value), ...)
        """
        user = self.getOne(ctx, uid)
        for attr, value in attrs.iteritems():
            user = self._validateUserAttribute(user, attr, value, log)
        return user

    def _validateUserAttribute(self, user, attr, value, log = True):
        return self._changeUserAttribute(user, attr, value, log)

    def _changeUserAttribute(self, user, attr, value, log = True):
        if user:
            if attr in self.attrs:
                # don't log jpeg values
                if log:
                    if attr == "jpegPhoto":
                        attrValue = None
                    else:
                        attrValue = value
                    r = AF().log(self.audit_plugin_name,
                                 self.audit_mod_attr,
                                 [(str(user.uid), AT.USER), (attr, AT.ATTRIBUTE)],
                                 attrValue)

                user.__setattr__(attr, value)
                user.save()
                if log:
                    r.commit()
                return user
        else:
            raise UserDoesNotExists()

    def canRemoveOne(self, ctx, uid):
        """
        Is the connected user allowed to remove uid user
        """
        return True

    def removeOne(self, ctx, uid):
        """
        Remove a user from the directory
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_DEL_USER, [(uid, AT.USER)])

        user = self.getOne(ctx, uid)
        # Remove the user from all groups
        LdapGroups().removeUserFromAll(ctx, user)
        # Finally delete the user
        user.delete()

        # Run hooks
        self.runHook("users.removeuser", uid)

        r.commit()
        return True


class PosixUsers(LdapUsers):

    attrs = ['uidNumber', # req
             'gidNumber', # req
             'homeDirectory', # req
             'loginShell',
             'gecos',
             'description']

    def addAttributes(self, uid, password, attrs = {}):
        """
        Add POSIX attributes to a user
        """
        user = self.getOne(None, uid)

        if not 'posixAccount' in user.objectClass:
            r = AF().log(PLUGIN_NAME, AA.USERS_ADD_USER_POSIX_ATTRS, [(uid, AT.USER)])
            # Check attributes
            if not 'homeDirectory' in attrs:
                attrs['homeDirectory'] = self._getHomeDir(uid, check_exists = True)
            else:
                attrs['homeDirectory'] = self._getHomeDir(uid,
                                                          attrs['homeDirectory'],
                                                          True)
            if not 'loginShell' in attrs:
                attrs['loginShell'] = self.config.login_shell

            attrs['uidNumber'] = self._getUID()

            if not 'primaryGroup' in attrs:
                attrs['primaryGroup'] = self.config.default_group
            attrs['gidNumber'] = self._getGID(attrs['primaryGroup'])

            if not 'gecos' in attrs:
                gecos = ""
                if 'givenName' in user:
                    gecos = str(user.givenName) + " "
                if 'sn' in user:
                    gecos += str(user.sn)
                attrs['gecos'] = delete_diacritics(gecos)
            else:
                attrs['gecos'] = delete_diacritics(attrs['gecos'])

            # Add objectClasses
            user.objectClass.append('posixAccount')
            # Fill attributes
            for attr, value in attrs.iteritems():
                if attr in self.attrs:
                    user.__setattr__(attr, value)
            user.save()
            r.commit()

        return user

    def removeAttributes(self, uid):
        """
        Remove all POSIX attributes from a user
        """
        user = self.getOne(None, uid)

        if 'posixAccount' in user.objectClass:
            r = AF().log(PLUGIN_NAME, AA.USERS_DEL_USER_POSIX_ATTRS, [(uid, AT.USER)])
            user.objectClass.remove('posixAccount')
            for attr in self.attrs:
                if attr in user:
                    user.__delattr__(attr)
            user.save()
            r.commit()

        return user

    def _getUID(self):
        uidNumber = self.config.uid_start - 1
        for user in self.getAll(None):
            if 'uidNumber' in user and int(str(user.uidNumber)) > uidNumber:
                    uidNumber = int(str(user.uidNumber))
        uidNumber += 1
        return str(uidNumber)

    def _getGID(self, group):
        return str(LdapGroups().getOne(None, group).gidNumber)

    def _getHomeDir(self, uid, home_dir = None, check_exists = True):
        """
        Check if home directory can be created
        """

        # Make a home string if none was given
        if not home_dir: home_dir = os.path.join(self.config.base_home_dir, uid)
        if not self._isAuthorizedHome(home_dir):
            raise Exception("%s is not an authorized home dir." % home_dir)
        # Return home dir path
        if check_exists:
            if not os.path.exists(home_dir):
                return home_dir
            else:
                raise Exception("%s already exists." % home_dir)
        else:
            return home_dir

    def _isAuthorizedHome(self, home_dir):
        for base_home in self.config.authorized_base_home_dir:
            if base_home in home_dir:
                return True
        return False

    def _validateAttribute(self, user, attr, value, log):
        if attr == 'homeDirectory':
            # Will raise an OSError exception if path doesn't exists
            os.stat(value)

        return self._changeUserAttribute(user, attr, value, log)

class LdapGroups(LdapConnection, GroupI):

    audit_plugin_name = PLUGIN_NAME
    audit_mod_attr = AA.USERS_MOD_GROUP_ATTR

    attrs = ['cn',
             'description',
             'uniqueMember',
             'gidNumber',
             'memberUid']

    def __init__(self):
        self.config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
        LdapConnection.__init__(self, self.config.uri, self.config.base,
                                self.config.login, self.config.password,
                                self.config.certfile)
        self.changeBase(str(self.getOU(self.config.groups_ou)))

    def canAdd(self, ctx):
        return True

    def canEdit(self, ctx):
        return True

    def canRemove(self, ctx):
        return True

    def getOne(self, ctx, cn):
        """
        Get group from the directory
        """
        # If cn is already an LdapNode
        # return it directly
        if isinstance(cn, ldapom.LdapNode):
            return cn
        # Search the group
        for group in self.search('cn=%s' % cn):
            return group
        raise GroupDoesNotExists()

    def getAll(self, ctx, search = "*", base = None):
        """
        Return the list of groups below the base
        """
        if not base: base = self._base
        filter = "(|(cn=%s)(description=%s))" % (search, search)
        return list(self.search(filter, base=base))

    def addOne(self, ctx, cn, attrs = {}, base = None):
        """
        Add posixGroup group to base
        """
        if not base: base = self._base

        r = AF().log(PLUGIN_NAME, AA.USERS_ADD_GROUP, [(cn, AT.GROUP)])

        try:
            group = self.getOne(ctx, cn)
            raise GroupAlreadyExists()
        except GroupDoesNotExists:
            # Create the group
            group = self.new_ldap_node('cn=%s,%s' % (cn, base))
            if self.config.type == "389DS":
                group.objectClass = ['groupOfUniqueNames', 'posixGroup', 'top']
            else:
                group.objectClass = ['namedObject', 'posixGroup', 'top']
            group.cn = cn
            if 'description' in attrs:
                group.description = attrs['description']
            group.gidNumber = self._getGID(ctx)
            group.save()
            r.commit()
            # Run hooks
            self.runHook("users.addgroup", cn)

            return group

    def _getGID(self, ctx):
        """
        Get next free gidNumber
        """
        gidNumber = self.config.gid_start - 1
        for group in self.getAll(ctx):
            if 'gidNumber' in group and int(str(group.gidNumber)) > gidNumber:
                    gidNumber = int(str(group.gidNumber))
        gidNumber += 1
        return str(gidNumber)

    def _isEmpty(self, group):
        """
        Returns true if the group has no members
        """
        if not 'uniqueMember' in group and not 'memberUid' in group:
            return True

        return False

    def addUser(self, ctx, cn, uid):
        """
        Add a user to a group
        """
        user = LdapUsers().getOne(ctx, uid)
        group = self.getOne(ctx, cn)

        r = AF().log(PLUGIN_NAME,
                     AA.USERS_ADD_USER_TO_GROUP,
                     [(str(group.cn), AT.GROUP), (str(user.uid), AT.USER)])

        # OpenLDAP // No Members
        if self.config.type == "OpenLDAP" and self._isEmpty(group):
            # We need to delete the group and recreate it
            # for changing the structural ObjectClass to groupOfUniqueNames
            dn = str(group)
            cn = str(group.cn)
            if 'description' in group:
                description = str(group.description)
            else:
                description = False
            gidNumber = str(group.gidNumber)
            group.delete()
            group = self.new_ldap_node(dn)
            group.objectClass = ['groupOfUniqueNames', 'posixGroup', 'top']
            group.cn = cn
            if description:
                group.description = description
            group.gidNumber = gidNumber
            group.uniqueMember = str(user)
            group.memberUid = str(user.uid)
            group.save()
        # 389DS // No Members
        elif self.config.type == "389DS" and self._isEmpty(group):
            group.uniqueMember = str(user)
            group.memberUid = str(user.uid)
            group.save()
        # We already have some members
        else:
            group.uniqueMember.append(str(user))
            group.memberUid.append(str(user.uid))
            group.save()

        r.commit()

        return group

    def removeUser(self, ctx, cn, uid):
        """
        Remove a user from a group
        """
        user = LdapUsers().getOne(ctx, uid)
        group = self.getOne(ctx, cn)

        # Is there members in that group ?
        if not self._isEmpty(group):
            r = AF().log(PLUGIN_NAME,
                         AA.USERS_DEL_USER_FROM_GROUP,
                         [(str(group.cn), AT.GROUP), (str(user.uid), AT.USER)])
            if 'uniqueMember' in group:
                group.uniqueMember.remove(str(user))
            if 'memberUid' in group:
                group.memberUid.remove(str(user.uid))
            # OpenLDAP
            # No more members switch back to namedObject
            # structural objectClass
            if self.config.type == "OpenLDAP" and len(group.uniqueMember) == 0:
                dn = str(group)
                cn = str(group.cn)
                if 'description' in group:
                    description = str(group.description)
                else:
                    description = False
                gidNumber = str(group.gidNumber)
                group.delete()
                group = self.new_ldap_node(dn)
                group.objectClass = ['namedObject', 'posixGroup', 'top']
                group.cn = cn
                if description:
                    group.description = description
                group.gidNumber = gidNumber
            # Save the group
            group.save()
            # FIXME Members not correctly updated in the object with 389DS
            group.retrieve_attributes()
            r.commit()

        return group

    def removeUserFromAll(self, ctx, uid):
        """
        Remove a user from all groups
        """
        user = LdapUsers().getOne(ctx, uid)

        r = AF().log(PLUGIN_NAME,
                     AA.USERS_DEL_USER_FROM_ALL_GROUPS,
                     [("", AT.GROUP), (str(user.uid), AT.USER)])

        for group in self.getAll(ctx):
            self.removeUser(ctx, group, user)

        r.commit()
        return True

    def changeAttributes(self, ctx, cn, attrs, log = True):
        """
        Change attributes of a group

        attrs: dict((attr, value), ...)
        """
        group = self.getOne(cn)
        for attr, value in attrs.iteritems():
            group = self._validateGroupAttribute(group, attr, value, log)
        return group

    def _validateGroupAttribute(self, group, attr, value, log = True):
        return self._changeGroupAttribute(group, attr, value, log)

    def _changeGroupAttribute(self, group, attr, value, log = True):
        if group:
            if attr in self.attrs:
                # don't log jpeg values
                if log:
                    r = AF().log(self.audit_plugin_name,
                                 self.audit_mod_attr,
                                 [(str(group.cn), AT.GROUP), (attr, AT.ATTRIBUTE)],
                                 value)

                group.__setattr__(attr, value)
                group.save()
                if log:
                    r.commit()
                return group
        else:
            raise GroupDoesNotExists()

    def removeOne(self, ctx, cn):
        """
        Remove a group from the directory
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_DEL_GROUP, [(cn, AT.GROUP)])

        cn = self.getOne(ctx, cn)
        cn.delete()

        # Run hooks
        self.runHook("users.removegroup", cn)

        r.commit()
        return True


# Posix user "submodule"
def addUserPosixAttributes(uid, password, attrs = {}):
    return PosixUsers().addAttributes(uid, password, attrs)
def changeUserPosixAttribute(uid, attr, value, log = True):
    return PosixUsers().changeUserAttribute(uid, attr, value, log)
def changeUserPosixAttributes(uid, attrs, log = True):
    return PosixUsers().changeUserAttributes(uid, attrs, log)
def removeUserPosixAttributes(uid):
    return PosixUsers().removeAttributes(uid)


# Exceptions for this plugin
class UsersExceptions(Exception):
    pass

class UserDoesNotExists(UsersExceptions):
    pass

class UserAlreadyExists(UsersExceptions):
    pass

class GroupDoesNotExists(UsersExceptions):
    pass

class GroupAlreadyExists(UsersExceptions):
    pass
