# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Configuration classes for the audit module.
"""

from mmc.support.config import PluginConfig

class AuditConfig(PluginConfig):

    """
    Parse the audit system configuration file.
    """

    def readConf(self):
        section = "audit"
        if self.has_section(section):
            self.auditmethod = self.get(section, "method")
            if self.auditmethod == "database":
                self.auditdbhost = self.get(section, "dbhost")
                self.auditdbport = self.getint(section, "dbport")
                self.auditdbuser = self.get(section, "dbuser")
                self.auditdbpassword = self.getpassword(section, "dbpassword")
                self.auditdbname = self.get(section, "dbname")
                self.auditdbdriver = self.get(section, "dbdriver")
