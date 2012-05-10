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

    def canEdit(self, ctx, uid):
        """
        Is the connected user allowed to edit uid
        """
        pass

    def canRemove(self, ctx, uid):
        """
        Is the connected user allowed to remove uid
        """
        pass

    def canChangePassword(self, ctx, uid):
        """
        Is the connected user allowed to change uid password 
        """
        pass

    def canChangeAttributes(self, ctx, uid):
        """
        Is the connected user allowed to change uid attributes
        """
        pass

    def canManageBases(self, ctx):
        """
        Is the connected user allowed to add or remove user bases 
        in the current backend
        """
        pass

    def canHaveGroups(self, ctx):
        """
        Does the backend handle user's groups
        """
        pass

    def getOne(self, ctx, uid):
        """
        Return user
        """
        pass

    def getACL(self, ctx, uid):
        """
        Return user MMC ACLs
        """
        pass

    def getGroups(self, ctx, uid):
        """
        Return user groups
        """
        pass

    def getAll(self, ctx, search = "*", base = None):
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

    def addOne(self, ctx, uid, password, properties = {}, base = None):
        """
        Add a user
        """
        pass

    def changePassword(self, ctx, uid, password, old_password = None, bind = False):
        """
        Change user password
        """
        pass

    def changeAttributes(self, ctx, uid, attrs, log = True):
        """
        Change user attributes
        """
        pass

    def removeOne(self, ctx, uid):
        """
        Remove user
        """
        pass

class GroupI:

    def canAdd(self, ctx):
        """
        Is the connected user allowed to add groups
        """
        pass

    def canEdit(self, ctx, name):
        """
        Is the connected user allowed to edit the group name
        """
        pass

    def canRemove(self, ctx, name):
        """
        Is the connected user allowed to remove the group name
        """
        pass

    def getOne(self, ctx, name):
        """
        Return group
        """
        pass

    def getAll(self, ctx, search = "*", base = None):
        """
        Return a list of groups
        """
        pass

    def addOne(self, ctx, name, attrs = {}, base = None):
        """
        Add a group name
        """
        pass

    def changeAttributes(self, ctx, name, attrs, log = True):
        """
        Change group attributes
        """
        pass

    def addUser(self, ctx, name, uid):
        """
        Add a user to the group name
        """
        pass

    def removeUser(self, ctx, name, uid):
        """
        Remove the user from the group name
        """
        pass

    def removeUserFromAll(self, ctx, uid):
        """
        Remove the user from all groups
        """
        pass

    def removeOne(self, ctx, name):
        """
        Remove the group name
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
        log.debug("Registering user manager %s / (%s, %s)" % (name, str(user_class), str(group_class)))
        self.components[name] = {}
        self.components[name]['user'] = user_class
        self.components[name]['group'] = group_class

    def validate(self):
        ret = (self.main == "none") or (self.main in self.components)
        if not ret:
            log.error("Selected user manager '%s' not available" % self.main)
            log.error("Please check that the corresponding plugin was successfully enabled")
        return ret

    def canUserHaveGroups(self, ctx):
        if self.components[self.main]['group']:
            return True
        return False

    def canAddUser(self, ctx):
        klass = self.components[self.main]['user']
        return klass().canAdd(ctx)

    def canEditUser(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().canEdit(ctx, uid)

    def canRemoveUser(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().canRemove(ctx, uid)

    def canChangeUserPassword(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().canChangePassword(ctx, uid)

    def canChangeUserAttributes(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().canChangeAttributes(ctx, uid)

    def canManageUserBases(self, ctx):
        klass = self.components[self.main]['user']
        return klass().canManageBases(ctx)

    def getUser(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().getOne(ctx, uid)

    def getUserACL(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().getACL(ctx, uid)

    def getUserGroups(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().getGroups(ctx, uid)

    def getUsers(self, ctx, search = "*", base = None):
        klass = self.components[self.main]['user']
        return klass().getAll(ctx, search, base)

    def addUserBase(self, ctx, name, base = None):
        klass = self.components[self.main]['user']
        return klass().addBase(ctx, name, base)

    def removeUserBase(self, ctx, name, recursive = False):
        klass = self.components[self.main]['user']
        return klass().removeBase(ctx, name)

    def addUser(self, ctx, uid, password, properties = {}, base = None):
        klass = self.components[self.main]['user']
        return klass().addOne(ctx, uid, password, properties, base)

    def changeUserPassword(self, ctx, uid, password, old_password = None, bind = False):
        klass = self.components[self.main]['user']
        return klass().changePassword(ctx, uid, password, old_password, bind)

    def changeUserAttributes(self, ctx, uid, attrs, log = True):
        klass = self.components[self.main]['user']
        return klass().changeAttributes(ctx, uid, attrs, log)

    def removeUser(self, ctx, uid):
        klass = self.components[self.main]['user']
        return klass().removeOne(ctx, uid)

    def canAddGroup(self, ctx):
        klass = self.components[self.main]['group']
        return klass().canAdd(ctx)

    def canEditGroup(self, ctx, name):
        klass = self.components[self.main]['group']
        return klass().canEdit(ctx)

    def canRemoveGroup(self, ctx, name):
        klass = self.components[self.main]['group']
        return klass().canRemove(ctx, name)

    def getGroup(self, ctx, name):
        klass = self.components[self.main]['group']
        return klass().getOne(ctx, name)

    def getGroups(self, ctx, search = "*", base = None):
        klass = self.components[self.main]['group']
        return klass().getAll(ctx, search, base)

    def addGroup(self, ctx, name, attrs = {}, base = None):
        klass = self.components[self.main]['group']
        return klass().addOne(ctx, name, attrs, base)

    def changeGroupAttributes(self, ctx, name, attrs, log = True):
        klass = self.components[self.main]['group']
        return klass().changeAttributes(ctx, name, attrs, log)

    def addGroupUser(self, ctx, name, uid):
        klass = self.components[self.main]['group']
        return klass().addUser(ctx, name, uid)

    def removeGroupUser(self, ctx, name, uid):
        klass = self.components[self.main]['group']
        return klass().removeUser(ctx, name, uid)

    def removeGroupUserFromAll(self, ctx, uid):
        klass = self.components[self.main]['group']
        return klass().removeUserFromAll(ctx, uid)

    def removeGroup(self, ctx, name):
        klass = self.components[self.main]['group']
        return klass().removeOne(ctx, name)
