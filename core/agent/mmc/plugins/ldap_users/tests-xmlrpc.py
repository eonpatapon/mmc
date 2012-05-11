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

import unittest2
from mmc.client import sync
from mmc.support.config import PluginConfigFactory
from mmc.plugins.ldap_users.config import LdapUsersConfig
from mmc.plugins.ldap_users import LdapUsers, LdapGroups
        
config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
proxy = sync.Proxy('https://mmc:s3cr3t@localhost:7080')
proxy.core.authenticate('root', config.password)

#class TestAuth(unittest.TestCase):
#
#    def setUp(self):
#        self.config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
#
#    def testPAMAuth(self):
#        self.assertTrue(proxy.core.authenticate('root', 'mandriva'))
#
#    def testLdapAuth(self):
#        self.assertFalse(proxy.core.authenticate('root', "sdjklfhskjdfhdksjh"))
#        self.assertTrue(proxy.core.authenticate('root', self.config.password))

class TestUsersGroups(unittest2.TestCase):

    def setUp(self):
        self.config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
        self.groups = LdapGroups()
        self.groups_ou = self.groups.addOU("groups_test")
        self.bg = str(self.groups_ou)
        self.users = LdapUsers()
        self.users_ou = self.users.addOU("users_tests")
        self.bu = str(self.users_ou)

    def testAddDelUser(self):
        self.assertEqual(proxy.core.getUsers("*", self.bu), [])
        user = proxy.core.addUser("user", "passééç", {'givenName': 'Test user'}, self.bu)
        self.assertEqual(user['uid'], "user")
        self.assertEqual(len(proxy.core.getUsers("*", self.bu)), 1)
        user = proxy.core.changeUserProperties('user', {'mail': "user@example.com"})
        self.assertEqual(user['uid'], "user")
        self.assertEqual(user['mail'], "user@example.com")
        user = proxy.core.changeUserProperties('user', {'preferredLanguage': "fr;en", 'mobile': "+336456789" })
        self.assertEqual(user['uid'], "user")
        self.assertEqual(user['mail'], "user@example.com")
        self.assertEqual(user['preferredLanguage'], "fr;en")
        self.assertEqual(user['mobile'], "+336456789")
        self.assertTrue(proxy.core.removeUser("user"))
        self.assertEqual(proxy.core.getUsers("*", self.bu), [])
    
    def testChangePassword(self):
        proxy.core.addUser("user", "passééç", {'givenName': 'Test user'}, self.bu)
        self.assertTrue(proxy.core.changeUserPassword("user", "pouet"))
        self.assertTrue(proxy.core.changeUserPassword("user", "withbind", "pouet", True))
        self.assertIn("ldap.INVALID_CREDENTIALS", proxy.core.changeUserPassword("user", "wrongpass", "foo", True)['faultCode'])

    def testAddDelGroup(self):
        self.assertEqual(len(proxy.core.getGroups("*", self.bg)), 0)
        nextGID = self.groups._getGID(None)
        group = proxy.core.addGroup("group", {'description': 'Test group', 'bad_attr': False }, self.bg)
        self.assertEqual(len(proxy.core.getGroups("*", self.bg)), 1)
        if self.config.type == "OpenLDAP":
            self.assertEqual(group['objectClass'], ['namedObject', 'posixGroup', 'top'])
        if self.config.type == "389DS":
            self.assertEqual(group['objectClass'], ['groupOfUniqueNames', 'posixGroup', 'top'])
        self.assertEqual(group['gidNumber'], nextGID)
        self.assertEqual(group['description'], "Test group")
        self.assertRaises(KeyError, group.__getitem__, 'bad_attr')
        self.assertTrue(proxy.core.removeGroup("group"))
        self.assertEqual(len(proxy.core.getGroups("*", self.bg)), 0)

    def testAddDelGroupUser(self):
        group = proxy.core.addGroup("group", {}, self.bg)
        proxy.core.addUser("user", "passééç", {'givenName': 'Test user'}, self.bu)
        group = proxy.core.addGroupUser("group", "user")
        self.assertEqual(group['objectClass'], ['groupOfUniqueNames', 'posixGroup', 'top'])
        self.assertEqual(group['memberUid'], 'user')
        self.assertEqual(group['uniqueMember'], 'uid=user,ou=users_tests,ou=People,dc=mandriva,dc=com')
        group = proxy.core.removeGroupUser("group", "user")
        if self.config.type == "OpenLDAP":
            self.assertEqual(group["objectClass"], ['namedObject', 'posixGroup', 'top'])
        if self.config.type == "389DS":
            self.assertEqual(group["objectClass"], ['groupOfUniqueNames', 'posixGroup', 'top'])
        self.assertRaises(KeyError, group.__getitem__, 'memberUid')
        self.assertRaises(KeyError, group.__getitem__, 'uniqueMember')

    def testAddWithNonExistantMember(self):
        proxy.core.addGroup("group", {'description': 'test group'}, self.bg)
        self.assertIn("ldap_users.UserDoesNotExists", proxy.core.addGroupUser("group", "user")['faultCode'])

    def testRemoveUserFromAll(self):
        proxy.core.addUser("user1", "pasééù", {'givenName': 'Test user 1'}, self.bu)
        proxy.core.addUser("user2", "pasééù", {'givenName': 'Test user 2'}, self.bu)
        proxy.core.addGroup("group1", {'description': 'Test group 1 héhé'}, self.bg)
        proxy.core.addGroupUser("group1", "user1")
        group = proxy.core.addGroupUser("group1", "user2")
        self.assertEqual(group['uniqueMember'], ['uid=user1,ou=users_tests,ou=People,dc=mandriva,dc=com', 'uid=user2,ou=users_tests,ou=People,dc=mandriva,dc=com'])
        self.assertEqual(group['memberUid'], ['user1', 'user2'])
        proxy.core.addGroup("group2", {'description': 'Test group 2'}, self.bg)
        proxy.core.addGroupUser("group2", "user1")
        proxy.core.removeGroupUserFromAll("user1")
        group1 = proxy.core.getGroup("group1")
        self.assertEqual(group1['uniqueMember'], 'uid=user2,ou=users_tests,ou=People,dc=mandriva,dc=com')
        self.assertEqual(group1['memberUid'], 'user2')
        group2 = proxy.core.getGroup("group2")
        self.assertRaises(KeyError, group2.__getitem__, 'uniqueMember')
        self.assertRaises(KeyError, group2.__getitem__, 'memberUid')

    def testGetuserGroups(self):
        proxy.core.addUser("user1", "pasééù", {'givenName': 'Test user 1'}, self.bu)
        proxy.core.addGroup("group1", {'description': 'Test group 1'}, self.bg)
        proxy.core.addGroup("group2", {'description': 'Test group 1'}, self.bg)
        proxy.core.addGroupUser("group1", "user1")
        proxy.core.addGroupUser("group2", "user1")
        groups = proxy.core.getUserGroups("user1")
        self.assertEqual(str(groups[0]['cn']), "group1")
        self.assertEqual(str(groups[1]['cn']), "group2")

    def testAddRemovePosixAttributes(self):
        proxy.core.addUser("user1", "pasééù", {'givenName': 'Test user 1'}, self.bu)
        proxy.core.addUser("user2", "pasééù", {'givenName': 'Test user 2', 'sn': "Éàù"}, self.bu)
        g = proxy.core.addGroup("group1", {'description': 'Test group 1'}, self.bg)
        self.assertEqual(g['gidNumber'], "10001")
        g = proxy.core.addGroup("group2", {'description': 'Test group 2'}, self.bg)
        self.assertEqual(g['gidNumber'], "10002")
        u = proxy.core.addUserExtension("posix", "user1", "", {"primaryGroup": "group1"})
        self.assertEqual(u['uidNumber'], "10000")
        self.assertEqual(u['gidNumber'], "10001")
        self.assertEqual(u['gecos'], "Test user 1 user1")
        u = proxy.core.addUserExtension("posix", "user2", "", {"primaryGroup": "group1"})
        self.assertEqual(u['uidNumber'], "10001")
        self.assertEqual(u['gidNumber'], "10001")
        self.assertEqual(u['gecos'], "Test user 2 Eau")
        u = proxy.core.removeUserExtension("posix", "user2")
        self.assertEqual(u['objectClass'], ['top', 'person', 'inetOrgPerson', 'organizationalPerson'])
        self.assertRaises(KeyError, u.__getitem__, "uidNumber")

    def testChangePosixAttributes(self):
        proxy.core.addUser("user1", "pasééù", {'givenName': 'Test user 1'}, self.bu)
        proxy.core.addGroup("group1", {'description': 'Test group 1'}, self.bg)
        proxy.core.addGroup("group2", {'description': 'Test group 2'}, self.bg)
        proxy.core.addUserExtension("posix", "user1", "", {"primaryGroup": "group1"})
        proxy.core.changeUserExtensionProps("posix", "user1", {"primaryGroup": "group2"}, True)
        u = proxy.core.changeUserExtensionProps("posix", "user1", {"uidNumber": "20000"}, True)
        self.assertEqual(u['uidNumber'], "20000")
        self.assertEqual(u['gidNumber'], "10002")

    def tearDown(self):
        self.groups.delete_r(self.groups_ou._dn)
        self.users.delete_r(self.users_ou._dn)


if __name__ == '__main__':
        unittest2.main()
