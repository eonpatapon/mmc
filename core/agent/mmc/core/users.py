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
User Manager is used to call methods giving informations on users whatever is the user backend.

"""

import logging
from mmc.support.mmctools import Singleton

log = logging.getLogger()


class UserI:

    def canAddOne(self, ctx):
        """
        Is the connected user allowed to add users
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

    def canRemoveOne(self, ctx, uid):
        """
        Is the connected user allowed to remove uid
        """
        pass

    def canAddBase(self, ctx):
        """
        Is the connected user allowed to add a user base in the current backend
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

    def register(self, name, klass):
        log.debug("Registering user manager %s / %s" % (name, str(klass)))
        self.components[name] = klass

    def validate(self):
        ret = (self.main == "none") or (self.main in self.components)
        if not ret:
            log.error("Selected user manager '%s' not available" % self.main)
            log.error("Please check that the corresponding plugin was successfully enabled")
        return ret

    def canAddOne(self, ctx):
        klass = self.components[self.main]
        return klass().canAddOne(ctx)

    def canChangePassword(self, ctx, uid):
        klass = self.components[self.main]
        return klass().canChangePassword(ctx, uid)

    def canChangeAttributes(self, ctx, uid):
        klass = self.components[self.main]
        return klass().canChangeAttributes(ctx, uid)

    def canRemoveOne(self, ctx, uid):
        klass = self.components[self.main]
        return klass().canRemoveOne(ctx, uid)

    def canAddBase(self, ctx):
        klass = self.components[self.main]
        return klass().canAddBase(ctx)

    def canHaveGroups(self, ctx):
        klass = self.components[self.main]
        return klass().canHaveGroups(ctx)

    def getOne(self, ctx, uid):
        klass = self.components[self.main]
        return klass().getOne(ctx, uid)

    def getACL(self, ctx, uid):
        klass = self.components[self.main]
        return klass().getACL(ctx, uid)

    def getGroups(self, ctx, uid):
        klass = self.components[self.main]
        return klass().getGroups(ctx, uid)

    def getAll(self, ctx, search = "*", base = None):
        klass = self.components[self.main]
        return klass().getAll(ctx, search, base)

    def addBase(self, ctx, name, base = None):
        klass = self.components[self.main]
        return klass().addBase(ctx, name, base)

    def addOne(self, ctx, uid, password, properties = {}, base = None):
        klass = self.components[self.main]
        return klass().addOne(ctx, uid, password, properties, base)

    def changePassword(self, ctx, uid, password, old_password = None, bind = False):
        klass = self.components[self.main]
        return klass().changePassword(ctx, uid, password, old_password, bind)

    def changeAttributes(self, ctx, uid, attrs, log = True):
        klass = self.components[self.main]
        return klass().changeAttributes(ctx, uid, attrs, log)

    def removeOne(self, ctx, uid):
        klass = self.components[self.main]
        return klass().removeOne(ctx, uid)
