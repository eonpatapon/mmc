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
import ldap
from mmc.support.config import PluginConfig

class LdapUsersConfig(PluginConfig):
    """
    Define values needed by the users plugin.
    """

    # UserManager backend name
    backend_name = "LDAP Users"
    # LDAP configuration
    type = 'OpenLDAP'
    uri = 'ldap://127.0.0.1:389'
    base = 'dc=mandriva,dc=com'
    login = 'cn=admin,dc=mandriva,dc=com'
    password = 'secret'
    certfile = None
    # LDAP config backend
    config_uri = 'ldapi:///'
    config_login = ''
    config_password = ''
    # Users
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
        Read configuration from plugins/ldap_users.ini
        """

        try:
            self.type = self.get("ldap", "type")
        except:
            pass
        if self.type not in ['OpenLDAP', '389DS']:
            raise LdapUsersConfigError("LDAP server type must be 'OpenLDAP' or \
                                        '389DS' (without quotes)")
        try:
            self.uri = self.get("ldap", "uri")
        except:
            pass
        try:
            self.base = self.getdn("ldap", "base")
        except ldap.LDAPError:
            raise LdapUsersConfigError("Wrong DN syntax : %s" % \
                                       self.get("ldap", "base"))
        except:
            pass
        try:
            self.login = self.getdn("ldap", "login")
        except ldap.LDAPError:
            raise LdapUsersConfigError("Wrong DN syntax : %s" % \
                                       self.get("ldap", "login"))
        except:
            pass
        try:
            self.password = self.get("ldap", "password")
        except:
            pass
        try:
            self.certfile = self.get("ldap", "certfile")
        except:
            pass
        try:
            self.users_ou = self.get("ldap", "usersOU")
        except:
            pass
        try:
            self.groups_ou = self.get("ldap", "groupsOU")
        except:
            pass
        try:
            self.config_uri = self.get("ldap_config", "uri")
        except:
            pass
        try:
            self.config_login = self.getdn("ldap_config", "login")
        except ldap.LDAPError:
            raise LdapUsersConfigError("Wrong DN syntax : %s" % \
                                       self.get("ldap_config", "login"))
        except:
            pass
        try:
            self.config_password = self.get("ldap_config", "password")
        except:
            pass
        try:
            self.backend_name = self.get("users", "name")
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
                raise LdapUsersConfigError("skel_dir does not exists")
        except:
            pass
        try:
            self.base_home_dir = self.get("posix", "baseHomeDir")
            if not os.path.exists(self.base_home_dir):
                raise LdapUsersConfigError("baseHomeDir does not exists")
        except:
            pass
        try:
            self.authorized_base_home_dir = self.get("posix", \
                            "authorizedBaseHomeDir").replace(' ','').split(',')
        except:
            pass
        try:
            self.default_group = self.get("posix", "defaultGroup")
        except:
            pass

class LdapUsersConfigError(Exception):
    pass
