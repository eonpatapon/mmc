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

    def getOne(self, ctx, uid):
        """
        Get a user
        """
        pass

    def getACL(self, ctx, uid):
        """
        Get ACLs of user
        """
        pass

    def getAll(self, ctx, search = "*", base = None):
        """
        Get a list of users
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

    def getOne(self, ctx, uid):
        klass = self.components[self.main]
        return klass().getOne(ctx, uid)

    def getACL(self, ctx, uid):
        klass = self.components[self.main]
        return klass().getACL(ctx, uid)

    def getAll(self, ctx, search, base):
        klass = self.components[self.main]
        return klass().getAll(ctx, search, base)

