# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
Computer Profile manager
provide methods to work with profile association with computers
"""

import logging
from pulse2.utils import Singleton
from twisted.internet import defer

class ComputerProfileManager(Singleton):
    components = {}
    main = 'dyngroup'

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def select(self, name):
        self.logger.info("Selecting computer profile manager: %s" % name)
        self.main = name

    def register(self, name, klass):
        self.logger.debug("Registering computer profile manager %s / %s" % (name, str(klass)))
        self.components[name] = klass

    def validate(self):
        return True

    ##############################
    def getProfileByNameImagingServer(self, name, is_uuid):
        klass = self.components[self.main]
        return klass().getProfileByNameImagingServer(name, is_uuid)

    def getProfileByName(self, name):
        pass

    def doesProfileExistsByName(self, name):
        pass

    def getProfileByUUID(self, uuid):
        klass = self.components[self.main]
        return klass().getProfileByUUID(uuid)

    def getProfileImagingServerUUID(self, uuid):
        klass = self.components[self.main]
        return klass().getProfileImagingServerUUID(uuid)

    def getComputersProfile(self, uuid):
        klass = self.components[self.main]
        return klass().getComputersProfile(uuid)

    def doesProfileExistsByUUID(self, uuid):
        pass

    def addComputersToProfile(self, ctx, computers_UUID, profile_UUID):
        " ask to all profile managers "
        ret = True
        def treatDeferList(result):
            ret = True
            for r in result:
                ret = ret and r
            return ret

        dl = []
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'addComputersToProfile'):
                d = defer.maybeDeferred(klass().addComputersToProfile, ctx, computers_UUID, profile_UUID)
                dl.append(d)
        deferred = defer.DeferredList(dl)
        deferred.addCallback(treatDeferList)
        return deferred

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        " ask to all profile managers "
        ret = True
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'delComputersFromProfile'):
                r = klass().delComputersFromProfile(computers_UUID, profile_UUID)
                ret = ret and r
        return ret

    def delProfile(self, profile_UUID):
        " ask to all profile managers to remove the profile "
        ret = True
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'delProfile'):
                r = klass().delProfile(profile_UUID)
                ret = ret and r
        return ret

    def isComputerInProfile(self, computer_UUID, profile_UUID):
        pass

    def getProfileContent(self, uuid):
        klass = self.components[self.main]
        return klass().getProfileContent(uuid)

    def getForbiddenComputersUUID(self, profile_UUID = None):
        " ask to all profile managers "
        ret = []
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'getForbiddenComputersUUID'):
                r = klass().getForbiddenComputersUUID(profile_UUID)
                ret.extend(r)
        return ret

    def areForbiddenComputers(self, computer_UUID):
        " ask to all profile managers "
        ret = []
        for mod in self.components:
            klass = self.components[mod]
            if hasattr(klass, 'areForbiddenComputers'):
                r = klass().areForbiddenComputers(computer_UUID)
                ret.extend(r)
        return ret


#    def isdyn_group(self, ctx, gid):
#        klass = self.components[self.main]
#        return klass().isdyn_group(ctx, gid)

class ComputerProfileI:
#    def isdyn_group(self, ctx, gid):
#        """
#        Says if the group is a dynamic group or not (return a bool)
#        """
#        pass

    def getProfileByName(self, name):
        """
        Get a profile given it's name
        """
        pass

    def getProfileByNameImagingServer(self, name, is_uuid):
        pass

    def doesProfileExistsByName(self, name):
        pass

    def getProfileByUUID(self, uuid):
        pass

    def getProfileImagingServerUUID(self, uuid):
        pass

    def getComputersProfile(self, uuid):
        pass

    def doesProfileExistsByUUID(self, uuid):
        pass

    def addComputersToProfile(self, ctx, computers_UUID, profile_UUID):
        pass

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        pass

    def delProfile(self, profile_UUID):
        pass

    def isComputerInProfile(self, computer_UUID, profile_UUID):
        pass

    def getProfileContent(self, uuid):
        pass

    def getForbiddenComputersUUID(self, profile_UUID = None):
        return []

    def areForbiddebComputers(self, computer_UUID):
        return []
