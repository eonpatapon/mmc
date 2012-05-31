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
User Manager is used to call methods giving informations on users whatever
is the user backend.

"""

import logging
from mmc.support.mmctools import Singleton

log = logging.getLogger()


class UserI:

    def canAdd(self, ctx):
        """
        Is the connected user allowed to add users
        """
        pass

    def canEdit(self, ctx, user):
        """
        Is the connected user allowed to edit user
        """
        pass

    def canRemove(self, ctx, user):
        """
        Is the connected user allowed to remove user
        """
        pass

    def canChangePassword(self, ctx, user):
        """
        Is the connected user allowed to change user password
        """
        pass

    def canManageBases(self, ctx):
        """
        Is the connected user allowed to add or remove user bases
        in the current backend
        """
        pass

    def getOne(self, ctx, user):
        """
        Return user
        """
        pass

    def getACL(self, ctx, user):
        """
        Return user MMC ACLs
        """
        pass

    def getGroups(self, ctx, user):
        """
        Return user groups
        """
        pass

    def getAll(self, ctx, search = "*", start = None, end = None, base = None):
        """
        Return a list of users
        """
        pass

    def addBase(self, ctx, name, base = None):
        """
        Add a user base to the current backend
        """
        pass

    def removeBase(self, ctx, name):
        """
        Remove a user base to the current backend
        """
        pass

    def addOne(self, ctx, user, password, properties = {}, base = None):
        """
        Add a user
        """
        pass

    def changePassword(self, ctx, user, password, old_password = None, bind = False):
        """
        Change user password
        """
        pass

    def changeProperties(self, ctx, user, props, log = True):
        """
        Change user attributes
        """
        pass

    def removeOne(self, ctx, user):
        """
        Remove user
        """
        pass


class UserExtensionI:

    def addProperties(self, ctx, user, password, props):
        """
        Add extension attributes on user user
        """
        pass

    def changeProperties(self, ctx, user, props, log = True):
        """
        Change extension attributes on user user
        """
        pass

    def removeProperties(self, ctx, user):
        """
        Remove extension attributes from user user
        """
        pass


class GroupI:

    def canAdd(self, ctx):
        """
        Is the connected user allowed to add groups
        """
        pass

    def canEdit(self, ctx, group):
        """
        Is the connected user allowed to edit the group
        """
        pass

    def canRemove(self, ctx, group):
        """
        Is the connected user allowed to remove the group
        """
        pass

    def getOne(self, ctx, group):
        """
        Return group
        """
        pass

    def getAll(self, ctx, search = "*", start = None, end = None, base = None):
        """
        Return a list of groups
        """
        pass

    def addOne(self, ctx, group, props = {}, base = None):
        """
        Add a group
        """
        pass

    def changeProperties(self, ctx, group, props, log = True):
        """
        Change group attributes
        """
        pass

    def addUser(self, ctx, group, user):
        """
        Add a user to the group
        """
        pass

    def removeUser(self, ctx, group, user):
        """
        Remove the user from the group
        """
        pass

    def removeUserFromAll(self, ctx, user):
        """
        Remove the user from all groups
        """
        pass

    def removeOne(self, ctx, group):
        """
        Remove the group
        """
        pass


class GroupExtensionI:

    def addProperties(self, ctx, group, props = {}):
        """
        Add extension attributes on group
        """
        pass

    def changeProperties(self, ctx, group, props, log = True):
        """
        Change extension attributes on group
        """
        pass

    def removeProperties(self, ctx, group):
        """
        Remove extension attributes from group
        """
        pass


class UserManager(Singleton):

    components = {}
    main = "none"

    def __init__(self):
        Singleton.__init__(self)

    def select(self, name):
        log.info("Selecting user manager: %s" % name)
        self.main = name

    def getManagerName(self):
        return self.main

    def isActivated(self):
        return (self.main != 'none')

    def register(self, name, user_class, group_class = None):
        log.debug("Registering user manager '%s' / (%s, %s)" % (name, str(user_class), str(group_class)))
        if not name in self.components:
            self.components[name] = {}
            self.components[name]['user_extensions'] = {}
            self.components[name]['group_extensions'] = {}
        self.components[name]['user'] = user_class
        self.components[name]['group'] = group_class

    def registerUserExtension(self, name, extension_name, user_extension_class):
        log.debug("Registering user extension '%s' for '%s' / %s" % (extension_name, name, str(user_extension_class)))
        if not name in self.components:
            self.components[name] = {}
            self.components[name]['user_extensions'] = {}
            self.components[name]['group_extensions'] = {}
        self.components[name]['user_extensions'][extension_name] = user_extension_class

    def registerGroupExtension(self, name, extension_name, group_extension_class):
        log.debug("Registering group extension '%s' for '%s' / %s" % (extension_name, name, str(group_extension_class)))
        if not name in self.components:
            self.components[name] = {}
            self.components[name]['user_extensions'] = {}
            self.components[name]['group_extensions'] = {}
        self.components[name]['group_extensions'][extension_name] = group_extension_class

    def validate(self):
        ret = (self.main == "none") or (self.main in self.components)
        if not ret:
            log.error("Selected user manager '%s' not available" % self.main)
            log.error("Please check that the corresponding plugin was successfully enabled")
        return ret

    def canUserHaveGroups(self):
        if self.components[self.main]['group']:
            return True
        return False

    def getUserExtensionsList(self):
        extensions = []
        for extension in self.components[self.main]['user_extensions'].iteritems():
            extensions.append(extension)
        return extensions

    def getGroupExtensionsList(self):
        extensions = []
        for extension in self.components[self.main]['group_extensions'].iteritems():
            extensions.append(extension)
        return extensions

    # User

    def canAddUser(self, ctx):
        klass = self.components[self.main]['user']
        return klass().canAdd(ctx)

    def canEditUser(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().canEdit(ctx, user)

    def canRemoveUser(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().canRemove(ctx, user)

    def canChangeUserPassword(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().canChangePassword(ctx, user)

    def canManageUserBases(self, ctx):
        klass = self.components[self.main]['user']
        return klass().canManageBases(ctx)

    def getUser(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().getOne(ctx, user)

    def getUserACL(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().getACL(ctx, user)

    def getUserGroups(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().getGroups(ctx, user)

    def getUsers(self, ctx, search = "*", start = None, end = None, base = None):
        klass = self.components[self.main]['user']
        return klass().getAll(ctx, search, start, end, base)

    def addUserBase(self, ctx, name, base = None):
        klass = self.components[self.main]['user']
        return klass().addBase(ctx, name, base)

    def removeUserBase(self, ctx, name, recursive = False):
        klass = self.components[self.main]['user']
        return klass().removeBase(ctx, name)

    def addUser(self, ctx, user, password, properties = {}, base = None):
        klass = self.components[self.main]['user']
        return klass().addOne(ctx, user, password, properties, base)

    def changeUserPassword(self, ctx, user, password, old_password = None, bind = False):
        klass = self.components[self.main]['user']
        return klass().changePassword(ctx, user, password, old_password, bind)

    def changeUserProperties(self, ctx, user, props, log = True):
        klass = self.components[self.main]['user']
        return klass().changeProperties(ctx, user, props, log)

    def removeUser(self, ctx, user):
        klass = self.components[self.main]['user']
        return klass().removeOne(ctx, user)

    # Groups

    def canAddGroup(self, ctx):
        klass = self.components[self.main]['group']
        return klass().canAdd(ctx)

    def canEditGroup(self, ctx, group):
        klass = self.components[self.main]['group']
        return klass().canEdit(ctx, group)

    def canRemoveGroup(self, ctx, group):
        klass = self.components[self.main]['group']
        return klass().canRemove(ctx, group)

    def getGroup(self, ctx, group):
        klass = self.components[self.main]['group']
        return klass().getOne(ctx, group)

    def getGroups(self, ctx, search = "*", start = None, end = None, base = None):
        klass = self.components[self.main]['group']
        return klass().getAll(ctx, search, start, end, base)

    def addGroup(self, ctx, group, props = {}, base = None):
        klass = self.components[self.main]['group']
        return klass().addOne(ctx, group, props, base)

    def addGroupUser(self, ctx, group, user):
        klass = self.components[self.main]['group']
        return klass().addUser(ctx, group, user)

    def removeGroupUser(self, ctx, group, user):
        klass = self.components[self.main]['group']
        return klass().removeUser(ctx, group, user)

    def removeGroupUserFromAll(self, ctx, user):
        klass = self.components[self.main]['group']
        return klass().removeUserFromAll(ctx, user)

    def removeGroup(self, ctx, group):
        klass = self.components[self.main]['group']
        return klass().removeOne(ctx, group)

    # User extensions

    def addUserExtension(self, ctx, name, user, password, props = {}):
        klass = self.components[self.main]['user_extensions'][name]
        return klass().addProperties(ctx, user, password, props)

    def changeUserExtensionProps(self, ctx, name, user, props, log = True):
        klass = self.components[self.main]['user_extensions'][name]
        return klass().changeProperties(ctx, user, props, log)

    def removeUserExtension(self, ctx, name, user):
        klass = self.components[self.main]['user_extensions'][name]
        return klass().removeProperties(ctx, user)

    # Group extensions

    def addGroupExtension(self, ctx, name, group, props = {}):
        klass = self.components[self.main]['group_extensions'][name]
        return klass().addProperties(ctx, group, props)

    def changeGroupExtensionProps(self, ctx, name, group, props, log = True):
        klass = self.components[self.main]['group_extensions'][name]
        return klass().changeProperties(ctx, group, props, log)

    def removeGroupExtension(self, ctx, name, group):
        klass = self.components[self.main]['group_extensions'][name]
        return klass().removeProperties(ctx, group)
