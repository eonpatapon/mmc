# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
#
# $Id: writers.py 4827 2009-11-27 14:54:51Z cdelfosse $
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
Contains constants for the audit system. 
"""

class AuditActions:
    # Users
    USERS_ADD_USER = u'USERS_ADD_USER'
    USERS_ADD_USER_POSIX_ATTRS = u'USERS_ADD_USER_POSIX_ATTRS'
    USERS_DEL_USER_POSIX_ATTRS = u'USERS_DEL_USER_POSIX_ATTRS'
    USERS_MOD_USER_ATTR = u'USERS_MOD_USER_ATTR'
    USERS_MOD_USER_PASSWORD = u'USERS_MOD_USER_PASSWORD'
    USERS_DEL_USER = u'USERS_DEL_USER'
    USERS_MOVE_USER_HOME = u'USERS_MOVE_USER_HOME'
    # Groups
    USERS_ADD_GROUP = u'USERS_ADD_GROUP'
    USERS_MOD_GROUP_ATTR = u'USERS_MOD_GROUP_ATTR'
    USERS_DEL_GROUP = u'USERS_DEL_GROUP'
    # Group operations
    USERS_ADD_USER_TO_GROUP = u'USERS_ADD_USER_TO_GROUP'
    USERS_DEL_USER_FROM_GROUP = u'USERS_DEL_USER_FROM_GROUP'
    USERS_DEL_USER_FROM_ALL_GROUPS = u'USERS_DEL_USER_FROM_ALL_GROUPS'
    # Add user OU
    USERS_ADD_USER_OU = u'USERS_ADD_USER_OU'
AA = AuditActions

class AuditTypes:
    USER = u'USER'
    GROUP = u'GROUP'
    ATTRIBUTE = u'ATTRIBUTE'
    ORGANIZATIONAL_UNIT = u'ORGANIZATIONAL_UNIT'
AT = AuditTypes

PLUGIN_NAME = u'MMC-USERS'
