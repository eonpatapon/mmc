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
from mmc.core.users import UserManager, UserI
from mmc.support import ldapom
from mmc.support.config import PluginConfigFactory
from mmc.support.mmctools import delete_diacritics
from mmc.plugins.users.audit import AA, AT, PLUGIN_NAME
from mmc.plugins.users.config import UsersConfig

VERSION = "3.0.3.2"
APIVERSION = "0:0:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

logger = logging.getLogger()

def activate():
    # Check LDAP credentials
    try:
        conn = LdapConnection()
    except ldap.INVALID_CREDENTIALS:
        logger.error("Can't bind to LDAP: invalid credentials.")
        return False
    # Check and load necessary schemas in LDAP
    try:
        schemas = os.path.join(datadir, 'doc', 'python-mmc-users', 'contrib')
        config = LdapConfigConnection()
        if not config.getSchema('mmc'):
            config.addSchema(os.path.join(schemas, 'mmc.ldif'))
        if not config.getSchema('rfc2307bis'):
            config.addSchema(os.path.join(schemas, 'rfc2307bis.ldif'))
    except:
        logger.warning("Can't access LDAP cn=config database.")
        try:
            schema = conn.getSchema("lmcUserObject")
            if len(schema) <= 0:
                logger.error("MMC schema seems not be include in LDAP directory.")
                return False
        except:
            logger.error("Invalid MMC schema.")
    # Create required OUs
    config = PluginConfigFactory.new(UsersConfig, "users")
    ous = [ config.users_ou, config.groups_ou ]
    for ou in ous:
        if not conn.getOU(ou):
            conn.addOU(ou)
    # Create the default group
    groups = Groups()
    try:
        groups.addOne(config.default_group)
        logger.info("Default user group %s created." % config.default_group)
    except GroupAlreadyExists:
        pass

    return True

def activate_2():
    UserManager().register("ldap", Users)
    UserManager().select("ldap")

    return True


class Users(LdapConnection, UserI):

    audit_plugin_name = PLUGIN_NAME
    audit_mod_attr = AA.USERS_MOD_USER_ATTR

    classes = ['top',
               'person',
               'inetOrgPerson',
               'lmcUserObject']
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
             'homePostalAddress',
             'lmcACL']

    def __init__(self):
        LdapConnection.__init__(self)
        self.config = PluginConfigFactory.new(UsersConfig, "users")
        # Limit queries to the users OU
        self.changeBase(str(self.getOU(self.config.users_ou)))

    def getOne(self, ctx, uid):
        """
        Get user from the directory
        """
        for user in self.search('uid=%s' % uid):
            return user
        if uid == "root":
            return self.retrieve_ldap_node(self.ldap_config.login)
        raise UserDoesNotExists()

    def getACL(self, ctx, uid):
        """
        Get user ACL from directory
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

    def addOU(self, ctx, name, base = None):
        """
        Add an OU for users
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_ADD_USER_OU, [(name, AT.ORGANIZATIONAL_UNIT)])
        ou = LdapConnection.addOU(self, name, base)
        r.commit()

        return ou

    def addOne(self, ctx, uid, password, attrs = {}, base = None):
        """
        Add inetOrgUser user to base
        """
        if not base: base = self._base;

        r = AF().log(PLUGIN_NAME, AA.USERS_ADD_USER, [(uid, AT.USER)])

        try:
            user = self.getOne(uid)
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
            self.changePassword(str(user.uid), password)
            # Run hooks
            self.runHook("users.adduser", uid, password)

            return user

    def getGroups(self, uid):
        """
        Get the user's groups
        """
        user = self.getOne(uid)
        groups = []
        for group in Groups().getAll():
            if 'member' in group and str(user) in group.member:
                groups.append(group)

        return groups

    def changePassword(self, uid, password, old_password = None, bind = False):
        """
        Change the user password using LDAP Password Modify Extended Operation
        """
        user = self.getOne(uid)
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

    def changeAttributes(self, uid, attrs, log = True):
        """
        Change attributes of a user

        attrs: dict((attr, value), ...)
        """
        user = self.getOne(uid)
        for attr, value in attrs.iteritems():
            user = self._validateUserAttribute(user, attr, value, log)
        return user

    def changeAttribute(self, uid, attr, value, log = True):
        user = self.getOne(uid)
        return self._validateUserAttribute(user, attr, value, log)

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

    def removeOne(self, uid):
        """
        Remove a user from the directory
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_DEL_USER, [(uid, AT.USER)])

        user = self.getOne(uid)
        # Remove the user from all groups
        Groups().removeUserFromAll(user.uid)
        # Finally delete the user
        user.delete()

        # Run hooks
        self.runHook("users.removeuser", uid)

        r.commit()


class PosixUsers(Users):

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
        user = self.getOne(uid)

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
        user = self.getOne(uid)

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
        for user in self.getAll():
            if 'uidNumber' in user and int(str(user.uidNumber)) > uidNumber:
                    uidNumber = int(str(user.uidNumber))
        uidNumber += 1
        return str(uidNumber)

    def _getGID(self, group):
        return str(Groups().getOne(group).gidNumber)

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

class Groups(LdapConnection):

    audit_plugin_name = PLUGIN_NAME
    audit_mod_attr = AA.USERS_MOD_GROUP_ATTR

    attrs = ['cn',
             'description',
             'member',
             'gidNumber',
             'memberUid']

    def __init__(self):
        LdapConnection.__init__(self)
        self.config = PluginConfigFactory.new(UsersConfig, "users")
        self.changeBase(str(self.getOU(self.config.groups_ou)))

    def getOne(self, cn):
        """
        Get group from the directory
        """
        for group in self.search('cn=%s' % cn):
            return group
        raise GroupDoesNotExists()

    def getAll(self, search = "*", base = None):
        """
        Return the list of groups below the base
        """
        if not base: base = self._base
        filter = "(|(cn=%s)(description=%s))" % (search, search)
        return list(self.search(filter, base=base))

    def addOne(self, cn, attrs = {}, base = None):
        """
        Add posixGroup group to base
        """
        if not base: base = self._base

        r = AF().log(PLUGIN_NAME, AA.USERS_ADD_GROUP, [(cn, AT.GROUP)])

        try:
            group = self.getOne(cn)
            raise GroupAlreadyExists()
        except GroupDoesNotExists:
            # Create the group
            group = self.new_ldap_node('cn=%s,%s' % (cn, base))
            group.objectClass = ['namedObject', 'posixGroup']
            group.cn = cn
            if 'description' in attrs:
                group.description = attrs['description']
            group.gidNumber = self._getGID()
            group.save()
            r.commit()
            # Run hooks
            self.runHook("users.addgroup", cn)

            return group

    def _getGID(self):
        """
        Get next free gidNumber
        """
        gidNumber = self.config.gid_start - 1
        for group in self.getAll():
            if 'gidNumber' in group and int(str(group.gidNumber)) > gidNumber:
                    gidNumber = int(str(group.gidNumber))
        gidNumber += 1
        return str(gidNumber)

    def addUser(self, cn, uid):
        """
        Add a user to a group
        """
        user = Users().getOne(uid)
        group = self.getOne(cn)
                
        r = AF().log(PLUGIN_NAME,
                     AA.USERS_ADD_USER_TO_GROUP,
                     [(str(group.cn), AT.GROUP), (str(user.uid), AT.USER)])

        # There is no members
        if not 'groupOfNames' in group.objectClass:
            # We need to delete the group and recreate it
            # for changing the structural ObjectClass to groupOfNames
            dn = str(group)
            cn = str(group.cn)
            if 'description' in group:
                description = str(group.description)
            else:
                description = False
            gidNumber = str(group.gidNumber)
            group.delete()
            group = self.new_ldap_node(dn) 
            group.objectClass = ['groupOfNames', 'posixGroup']
            group.cn = cn
            if description:
                group.description = description
            group.gidNumber = gidNumber
            group.member = str(user)
            group.memberUid = str(user.uid)

            group.save()
        else:
            group.member.append(str(user))
            group.memberUid.append(str(user.uid))
            group.save()

        r.commit()

        return group

    def removeUser(self, cn, uid):
        """
        Remove a user from a group
        """
        user = Users().getOne(uid)
        group = self.getOne(cn)

        if 'groupOfNames' in group.objectClass:
            r = AF().log(PLUGIN_NAME,
                         AA.USERS_DEL_USER_FROM_GROUP,
                         [(str(group.cn), AT.GROUP), (str(user.uid), AT.USER)])
            group.member.remove(str(user))
            group.memberUid.remove(str(user.uid))
            # No more members switch back to namedObject
            # structural objectClass
            if len(group.member) == 0:
                dn = str(group)
                cn = str(group.cn)
                if 'description' in group:
                    description = str(group.description)
                else:
                    description = False
                gidNumber = str(group.gidNumber)
                group.delete()
                group = self.new_ldap_node(dn) 
                group.objectClass = ['namedObject', 'posixGroup']
                group.cn = cn
                if description:
                    group.description = description
                group.gidNumber = gidNumber
            # Save the group
            group.save()
            r.commit()
        
        return group

    def removeUserFromAll(self, uid):
        """
        Remove a user from all groups
        """
        user = Users().getOne(uid)

        r = AF().log(PLUGIN_NAME,
                     AA.USERS_DEL_USER_FROM_ALL_GROUPS,
                     [("", AT.GROUP), (str(user.uid), AT.USER)])

        for group in self.getAll():
            self.removeUser(str(group.cn), str(user.uid))

        r.commit()
        return True

    def changeAttributes(self, cn, attrs, log = True):
        """
        Change attributes of a group

        attrs: dict((attr, value), ...)
        """
        group = self.getOne(cn)
        for attr, value in attrs.iteritems():
            group = self._validateGroupAttribute(group, attr, value, log)
        return group

    def changeAttribute(self, cn, attr, value, log = True):
        group = self.getOne(cn)
        return self._validateGroupAttribute(group, attr, value, log)

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

    def removeOne(self, cn):
        """
        Remove a group from the directory
        """
        r = AF().log(PLUGIN_NAME, AA.USERS_DEL_GROUP, [(cn, AT.GROUP)])

        cn = self.getOne(cn)
        cn.delete()

        # Run hooks
        self.runHook("users.removegroup", cn)

        r.commit()


# Posix user "submodule"
def addUserPosixAttributes(uid, password, attrs = {}):
    return PosixUsers().addAttributes(uid, password, attrs)
def changeUserPosixAttribute(uid, attr, value, log = True):
    return PosixUsers().changeUserAttribute(uid, attr, value, log)
def changeUserPosixAttributes(uid, attrs, log = True):
    return PosixUsers().changeUserAttributes(uid, attrs, log)
def removeUserPosixAttributes(uid):
    return PosixUsers().removeAttributes(uid)
# Groups
def getGroup(cn):
    return Groups().getOne(cn)
def getGroups(search = "*", base = None):
    return Groups().getAll(search, base)
def addGroup(cn, attrs = {}, base = None):
    return Groups().addOne(cn, attrs, base)
def changeGroupAttribute(cn, attr, value, log = True):
    return Groups().changeAttribute(cn, attr, value, log)
def changeGroupsAttributes(cn, attrs, log = True):
    return Groups().changeAttributes(cn, attrs, log)
def addGroupUser(cn, uid):
    return Groups().addUser(cn, uid)
def removeGroupUser(cn, uid):
    return Groups().removeUser(cn, uid)
def removeGroupsUser(uid):
    return Groups().removeUserFromAll(uid)
def removeGroup(cn):
    return Groups().removeOne(cn)


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
