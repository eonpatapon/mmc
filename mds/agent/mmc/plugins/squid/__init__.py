# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
MDS squid plugin for the MMC agent.
"""

import os
import logging
import ldap
from ConfigParser import NoSectionError, NoOptionError

from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory as AF
from mmc.support.config import PluginConfig, ConfigException
from mmc.plugins.squid.audit import AT, AA, PLUGIN_NAME
from mmc.plugins.base import createGroup, changeGroupDescription

logger = logging.getLogger()

VERSION = "0.0.1"
APIVERSION = "1:1:0"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    """
     this function define if the module "squid" can be activated.
     @return: return True if this module can be activate
     @rtype: boolean
    """
    config = ProxyConfig("squid")
    if config.disabled:
        logger.warning("Plugin squid: disabled by configuration.")
        return False

    #try:
    config.check()
    #except Exception, e:
        #logger.error("Squid configuration error: %s" % str(e))
        #return False

    return True


def reloadSquid():
    return ManageList().reloadSquid()

def stopSquid():
    return ManageList().stopSquid()

def startSquid():
    return ManageList().startSquid()

def genSarg():
    return ManageList().genSarg()

def cleanSarg():
    return ManageList().cleanSarg()

def getStatutProxy():
    return ManageList().getStatutProxy()

def getNormalBlacklist():
    return ManageList().getNormalBlacklist()

def getNormalWhitelist():
    return ManageList().getNormalWhitelist()

def getNormalExtlist():
    return ManageList().getNormalExtlist()

def addNormalBlacklist(elt):
    return ManageList().addNormalBlacklist(elt)

def delNormalBlacklist(elt):
    return ManageList().delNormalBlacklist(elt)

def addNormalWhitelist(elt):
    return ManageList().addNormalWhitelist(elt)

def delNormalWhitelist(elt):
    return ManageList().delNormalWhitelist(elt)

def addNormalExtlist(elt):
    return ManageList().addNormalBlackExt(elt)

def delNormalExtlist(elt):
    return ManageList().delNormalBlackExt(elt)

def getNormalTimelist():
    return ManageList().getTimeDaylist()

def addNormalTimelist(elt):
    return ManageList().addNormalTimelist(elt)

def delNormalTimelist(elt):
    return ManageList().delTimeDay(elt)


def getNormalMachlist():
    return ManageList().getNormalMachlist()

def addNormalMachlist(elt):
    return ManageList().addNormalMachlist(elt)

def delNormalMachlist(elt):
    return ManageList().delNormalMachlist(elt)


class ProxyConfig(PluginConfig):

    def readConf(self):

        PluginConfig.readConf(self)

        try: self.squidBinary = self.get("squid", "squidBinary")
        except (NoSectionError, NoOptionError): self.squidBinary = "/usr/sbin/squid"

        try: self.squidRules = self.get("squid", "squidRules")
        except (NoSectionError, NoOptionError): self.squidRules = "/etc/rules"

        try: self.squidMasterGroup = self.get("squid", "squidMasterGroup")
        except (NoSectionError, NoOptionError): self.squidMasterGroup = "/etc/rules/group_internet"

        try: self.normalBlackList = self.get("squid", "normalBlackList")
        except (NoSectionError, NoOptionError): self.normalBlackList = "/etc/rules/group_internet/normal_blacklist.txt"

        try: self.normalWhiteList = self.get("squid", "normalWhiteList")
        except (NoSectionError, NoOptionError): self.normalWhiteList = "/etc/rules/group_internet/normal_whitelist.txt"

        try: self.normalBlackExt = self.get("squid", "normalBlackExt")
        except (NoSectionError, NoOptionError): self.normalBlackExt = "/etc/rules/group_internet/normal_blacklist_ext.txt"

        try: self.timeDay = self.get("squid", "timeDay")
        except (NoSectionError, NoOptionError): self.timeDay = "/etc/rules/group_internet/time_day.txt"

        try: self.normalMachList = self.get("squid", "normalMachList")
        except (NoSectionError, NoOptionError): self.normalMachList = "/etc/rules/group_internet/allow_machines.txt"

        try: self.sargBinary = self.get("squid", "sargBinary")
        except (NoSectionError, NoOptionError): self.sargBinary = "/usr/bin/sarg"

        try: self.squidInit = self.get("squid", "squidInit")
        except (NoSectionError, NoOptionError): self.squidInit = "/etc/init.d/squid"

        try: self.squidPid = self.get("squid", "squidPid")
        except (NoSectionError, NoOptionError): self.squidPid = "/var/run/squid.pid"

        try: self.groupMaster = self.get("squid", "groupMaster")
        except (NoSectionError, NoOptionError): self.groupMaster = "Internet Master"
        self.groupMasterDesc = "Free access to Internet and downloads"

        try: self.groupFiltered = self.get("squid", "groupFiltered")
        except (NoSectionError, NoOptionError): self.groupFiltered = "Internet Filtered"
        self.groupFilteredDesc = "Filtered access to Internet and downloads"

        try: self.groupTime = self.get("squid", "groupTime")
        except (NoSectionError, NoOptionError): self.groupTime = "Internet Time"
        self.groupTimeDesc = "Access to Internet in specific hours"

    def check(self):
        if not os.path.exists(self.squidBinary):
            raise ConfigException("Can't find squid binary: %s" % self.squidBinary)

        if not os.path.exists(self.sargBinary):
            raise ConfigException("Can't find sarg binary: %s" % self.sargBinary)

        for dir in (self.squidRules, self.squidMasterGroup):
            if not os.path.exists(dir):
                logger.info("Creating %s" % dir)
                os.makedirs(dir)

        for list in (self.normalBlackList, self.normalWhiteList, self.normalBlackExt,
                     self.timeDay, self.normalMachList):
            if not os.path.exists(list):
                logger.info("Creating %s" % list)
                open(list, "w+").close()

        for group, desc in ((self.groupMaster, self.groupMasterDesc),
                            (self.groupFiltered, self.groupFilteredDesc),
                            (self.groupTime, self.groupTimeDesc)):
            try:
                createGroup(group)
                changeGroupDescription(group, desc)
                logger.info("Group %s created." % group)
            except ldap.ALREADY_EXISTS:
                pass



####################################################################
#           Class to persist and manipulate squid files
####################################################################

class ManageList:

    def __init__(self):
        """
        For easier modification Arrays are always loaded

        """
        self.config = ProxyConfig("squid")
        self.normalBlackList = self.config.normalBlackList
        self.normalWhiteList = self.config.normalWhiteList
        self.normalMachList = self.config.normalMachList
        self.normalBlackExt = self.config.normalBlackExt
        self.normal = self.config.normalBlackExt
        self.squid = self.config.squidBinary
        self.timeDay = self.config.timeDay
        self.squidInit = self.config.squidInit
        self.squidPid = self.config.squidPid
        self.sargBinary = self.config.sargBinary

        """Array to manipulate Nomal Black List"""
        self.contentArrNBL = []
        f = open(self.normalBlackList)
        for line in f:
            line = line.strip()
            if line and line not in self.contentArrNBL:
                self.contentArrNBL.append(line)
        f.close()

        """Array to manipulate Nomal White List"""
        self.contentArrNWL = []
        f = open(self.normalWhiteList)
        for line in f:
            line = line.strip()
            if line and line not in self.contentArrNWL:
                self.contentArrNWL.append(line)
        f.close()

        """Array to manipulate Nomal Black Extensions"""
        self.contentArrNBX = []
        f = open(self.normalBlackExt)
        for line in f:
            line = line.strip()
            if line and line not in self.contentArrNBX:
                self.contentArrNBX.append(line)
        f.close()

        """Array to manipulate Time day hour"""
        self.contentArrTDL = []
        f = open(self.timeDay)
        for line in f:
            line = line.strip()
            if line and line not in self.contentArrTDL:
                self.contentArrTDL.append(line)
        f.close()

        """Array to manipulate Time day hour"""
        self.contentArrML = []
        f = open(self.normalMachList)
        for line in f:
            line = line.strip()
            if line and line not in self.contentArrML:
               self.contentArrML.append(line)
        f.close()

    def reloadSquid(self):
        try:
            from mmc.plugins.services.manager import ServiceManager
            ServiceManager().reload("squid")
        except ImportError:
            from mmc.support.mmctools import ServiceManager
            SM = ServiceManager(self.squidInit, self.squidPid)
            SM.reload()

    def getStatutProxy(self):
        res={}
        res['squid']=0

        psout = os.popen('ps ax | grep squid | grep -v grep','r')
        try:
            tmp=psout.read()
        except:
            return res

        for a in tmp.split("\n"):
            if 'squid' in a : res['squid'] = 1
        psout.close()
        return res

    def getNormalBlacklist(self):
        return self.contentArrNBL

    def getNormalWhitelist(self):
        return self.contentArrNWL

    def getNormalExtlist(self):
        return self.contentArrNBX

    def getNormalTimelist(self):
        return self.contentArrNT

    def getNormalMachlist(self):
        return self.contentArrML

    def getTimeDaylist(self):
        return self.contentArrTDL

    def saveNormalBlacklist(self):
        f = open(self.config.normalBlackList, 'w')
        for elt in self.contentArrNBL:
            f.write(elt + '\n')
        f.close()
        return 0

    def saveNormalWhitelist(self):
        f = open(self.config.normalWhiteList, 'w')
        for elt in self.contentArrNWL:
            f.write(elt + '\n')
        f.close()
        return 0

    def saveNormalBlackExt(self):
        f = open(self.config.normalBlackExt, 'w')
        for elt in self.contentArrNBX:
            f.write(elt + '\n')
        f.close()
        return 0

    def addNormalBlacklist(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_ADD_NORMAL_BLACKLIST, [(elt, AT.AUDITLIST)])
        if not elt in self.contentArrNBL:
            self.contentArrNBL.append(elt)
        self.saveNormalBlacklist()
        r.commit()

    def delNormalBlacklist(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_DEL_NORMAL_BLACKLIST, [(elt, AT.AUDITLIST)])
        if elt in self.contentArrNBL:
            self.contentArrNBL.remove(elt)
        self.saveNormalBlacklist()
        r.commit()

    def addNormalWhitelist(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_ADD_NORMAL_WHITELIST, [(elt, AT.AUDITLIST)])
        if not elt in self.contentArrNWL:
            self.contentArrNWL.append(elt)
        self.saveNormalWhitelist()
        r.commit()

    def delNormalWhitelist(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_DEL_NORMAL_WHITELIST, [(elt, AT.AUDITLIST)])
        if elt in self.contentArrNWL:
            self.contentArrNWL.remove(elt)
        self.saveNormalWhitelist()
        r.commit()

    def addNormalBlackExt(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_ADD_NORMAL_BLACKEXT, [(elt, AT.AUDITLIST)])
        if not elt in self.contentArrNBX:
            self.contentArrNBX.append(elt)
        self.saveNormalBlackExt()
        r.commit()

    def delNormalBlackExt(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_DEL_NORMAL_BLACKEXT, [(elt, AT.AUDITLIST)])
        if elt in self.contentArrNBX:
            self.contentArrNBX.remove(elt)
        self.saveNormalBlackExt()
        r.commit()

    def saveTimeDaylist(self):
        f = open(self.config.timeDay, 'w')
        for elt in self.contentArrTDL:
            f.write(elt + '\n')
        f.close()
        return 0

    def addNormalTimelist(self, elt):
        """Add an element to the blacklist"""
        r = AF().log(PLUGIN_NAME, AA.PROXY_ADD_TIME_DAY, [(elt, AT.AUDITLIST)])
        if not elt in self.contentArrTDL:
            self.contentArrTDL.append(elt)
        self.saveTimeDaylist()
        r.commit()

    def delTimeDay(self, elt):
        """Remove an element from the blacklist"""
        r = AF().log(PLUGIN_NAME, AA.PROXY_DEL_TIME_DAY, [(elt, AT.AUDITLIST)])
        if elt in self.contentArrTDL:
            self.contentArrTDL.remove(elt)
        self.saveTimeDaylist()
        r.commit()

    def saveNormalMachlist(self):
        f = open(self.config.normalMachList, 'w')
        for elt in self.contentArrML:
            f.write(elt + '\n')
        f.close()
        return 0

    def addNormalMachlist(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_ADD_TIME_DAY, [(elt, AT.AUDITLIST)])
        if not elt in self.contentArrML:
            self.contentArrML.append(elt)
        self.saveNormalMachlist()
        r.commit()

    def delNormalMachlist(self, elt):
        r = AF().log(PLUGIN_NAME, AA.PROXY_ADD_TIME_DAY, [(elt, AT.AUDITLIST)])
        if elt in self.contentArrML:
           self.contentArrML.remove(elt)
        self.saveNormalMachlist()
        r.commit()
