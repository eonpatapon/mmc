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
from mmc.support.config import PluginConfig

class UsersConfig(PluginConfig):
    """
    Define values needed by the users plugin.
    """

    # Backend name
    backend_name = 'LDAP users'
    # Base
    users_ou = 'People'
    groups_ou = 'Group'
    # Posix
    uid_start = 10000
    gid_start = 10000
    default_group = "Users"
    login_shell = '/bin/bash'
    skel_dir = '/etc/skel'
    base_home_dir = '/home'
    authorized_base_home_dir = ['/home']

    def readConf(self):
        """
        Read configuration from plugins/users.ini
        """

        try:
            self.backend_name = self.get("main", "backendName")
        except:
            pass
        try:
            self.users_ou = self.get("main", "usersOU")
        except:
            pass
        try:
            self.groups_ou = self.get("main", "groupsOU")
        except:
            pass
        try:
            self.uid_start = self.getint("posix", "uidStart")
        except:
            pass
        try:
            self.gid_start = self.getint("posix", "gidStart")
        except:
            pass
        try:
            self.login_shell = self.get("posix", "loginShell")
        except:
            pass
        try:
            self.skel_dir = self.get("posix", "skelDir")
            if not os.path.exists(self.skel_dir):
                raise UsersConfigError("skel_dir does not exists")
        except:
            pass
        try:
            self.base_home_dir = self.get("posix", "baseHomeDir")
            if not os.path.exists(self.base_home_dir):
                raise UsersConfigError("baseHomeDir does not exists")
        except:
            pass
        try:
            self.authorized_base_home_dir = self.get("posix", "authorizedBaseHomeDir").replace(' ','').split(',')
        except:
            pass
        try:
            self.default_group = self.get("posix", "defaultGroup")
        except:
            pass

class UsersConfigError(Exception):
    pass
