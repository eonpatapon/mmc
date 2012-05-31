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

import unittest

from mmc.support.config import PluginConfigFactory
from mmc.plugins.ldap_users.config import LdapUsersConfig
from mmc.plugins.ldap_users import LdapUsers, LdapPosixUsers, \
                                   UserDoesNotExists, LdapGroups

class TestUsersGroups(unittest.TestCase):

    def setUp(self):
        self.config = PluginConfigFactory.new(LdapUsersConfig, "ldap_users")
        self.groups = LdapGroups()
        self.groups_ou = self.groups.addOU("groups_test")
        self.groups.changeBase(self.groups_ou._dn)
        self.users = LdapUsers()
        self.posix_users = LdapPosixUsers()
        self.users_ou = self.users.addOU("users_tests")
        self.users.changeBase(self.users_ou._dn)

    def testAddDelUser(self):
        u = self.users.addOne(None, "user", "pasééù", {'givenName': 'Test user'})
        self.assertEqual(str(u.uid), 'user')
        self.assertTrue(u.check_password('pasééù'))
        self.assertEqual(self.users.getAll(None)[0], 1)
        self.assertEqual(len(self.users.getAll(None)[1]), 1)
        self.users.changeProperties(None, 'user', {'mail': 'user@example.com'})
        # update our current object
        u.retrieve_attributes()
        self.assertEqual(str(u.mail), 'user@example.com')
        self.users.changeProperties(None, 'user', {'preferredLanguage': 'fr;en', 'mobile': '+336456789' })
        u.retrieve_attributes()
        self.assertEqual(unicode(u.preferredLanguage), u"fr;en")
        self.assertEqual(unicode(u.mobile), u"+336456789")
        self.users.removeOne(None, 'user')
        self.assertFalse(self.users.check_if_dn_exists(u._dn))

    def testChangePassword(self):
        u = self.users.addOne(None, "user", "pasééù", {'givenName': 'Test user'})
        self.assertTrue(u.check_password('pasééù'))
        u = self.users.changePassword(None, "user", "plop")
        self.assertTrue(u.check_password('plop'))
        u = self.users.changePassword(None, "user", "pouetéé", "plop", True)
        self.assertTrue(u.check_password('pouetéé'))

    def testAddDelGroup(self):
        g = self.groups.addOne(None, "group", {'description': 'Test group', 
                                               'bad_attr': False })
        if self.config.type == "OpenLDAP":
            self.assertEqual(list(g.objectClass), [u'namedObject', u'posixGroup', u'top'])
        if self.config.type == "389DS":
            self.assertEqual(list(g.objectClass), [u'groupOfUniqueNames', u'posixGroup', u'top'])
        self.assertEqual(str(g.gidNumber), "10000")
        self.assertEqual(str(g.description), 'Test group')
        self.assertRaises(AttributeError, g.__getattr__, 'bad_attr')
        self.groups.removeOne(None, 'group')
        self.assertFalse(self.groups.check_if_dn_exists(g._dn))

    def testAddDelGroupUser(self):
        self.groups.addOne(None, "GrOUp5TesT")
        self.users.addOne(None, "UsEr1TesT", "pasééù", {'givenName': 'Test user'})
        g = self.groups.addUser(None, "GrOUp5TesT", "UsEr1TesT")
        self.assertEqual(list(g.objectClass), [u'groupOfUniqueNames', u'posixGroup', u'top'])
        self.assertEqual(str(g.memberUid), 'UsEr1TesT')
        self.assertEqual(str(g.uniqueMember), 'uid=UsEr1TesT,ou=users_tests,ou=People,dc=mandriva,dc=com')
        g = self.groups.removeUser(None, "GrOUp5TesT", "UsEr1TesT")
        if self.config.type == "OpenLDAP":
            self.assertEqual(list(g.objectClass), [u'namedObject', u'posixGroup', u'top'])
        if self.config.type == "389DS":
            self.assertEqual(list(g.objectClass), [u'groupOfUniqueNames', u'posixGroup', u'top'])
        self.assertRaises(AttributeError, g.__getattr__, 'memberUid')
        self.assertRaises(AttributeError, g.__getattr__, 'uniqueMember')

    def testAddWithNonExistantMember(self):
        self.groups.addOne(None, "group", {'description': 'test group'})
        self.assertRaises(UserDoesNotExists, self.groups.addUser, None, "group", "user")

    def testRemoveUserFromAll(self):
        self.users.addOne(None, "UsEr1TesT", "pasééù", {'givenName': 'Test user 1'})
        self.users.addOne(None, "UsEr2TesT", "pasééù", {'givenName': 'Test user 2'})
        self.groups.addOne(None, "GrOUp1TesT", {'description': 'Test group 1 héhé'})
        self.groups.addUser(None, "GrOUp1TesT", "UsEr1TesT")
        g = self.groups.addUser(None, "GrOUp1TesT", "UsEr2TesT")
        self.assertEqual(list(g.uniqueMember), [u'uid=UsEr1TesT,ou=users_tests,ou=People,dc=mandriva,dc=com', u'uid=UsEr2TesT,ou=users_tests,ou=People,dc=mandriva,dc=com'])
        self.assertEqual(list(g.memberUid), [u'UsEr1TesT', u'UsEr2TesT'])
        self.groups.addOne(None, "GrOUp2TesT", {'description': 'Test group 2'})
        self.groups.addUser(None, "GrOUp2TesT", "UsEr1TesT")
        self.groups.removeUserFromAll(None, "UsEr1TesT")
        g = self.groups.getOne(None, 'GrOUp1TesT')
        self.assertEqual(list(g.uniqueMember), [u'uid=UsEr2TesT,ou=users_tests,ou=People,dc=mandriva,dc=com'])
        self.assertEqual(list(g.memberUid), [u'UsEr2TesT'])
        g = self.groups.getOne(None, 'GrOUp2TesT')
        self.assertRaises(AttributeError, g.__getattr__, 'uniqueMember')
        self.assertRaises(AttributeError, g.__getattr__, 'memberUid')

    def testGetuserGroups(self):
        self.users.addOne(None, "UsEr1TesT", "pasééù", {'givenName': 'Test user 1'})
        self.groups.addOne(None, "GrOUp1TesT", {'description': 'Test group 1'})
        self.groups.addOne(None, "GrOUp2TesT", {'description': 'Test group 1'})
        self.groups.addUser(None, "GrOUp1TesT", "UsEr1TesT")
        self.groups.addUser(None, "GrOUp2TesT", "UsEr1TesT")
        groups = self.users.getGroups(None, "UsEr1TesT")
        self.assertEqual(str(groups[0].cn), "GrOUp1TesT")
        self.assertEqual(str(groups[1].cn), "GrOUp2TesT")

    def testAddRemovePosixAttributes(self):
        self.users.addOne(None, "UsEr1TesT", "pasééù", {'givenName': 'Test user 1'})
        self.users.addOne(None, "UsEr2TesT", "pasééù", {'givenName': 'Test user 2', 'sn': "Éàù"})
        nextGID1 = self.groups._getGID(None)
        g = self.groups.addOne(None, "GrOUp1TesT", {'description': 'Test group 1'})
        self.assertEqual(str(g.gidNumber), nextGID1)
        nextGID2 = self.groups._getGID(None)
        g = self.groups.addOne(None, "GrOUp2TesT", {'description': 'Test group 2'})
        self.assertEqual(str(g.gidNumber), nextGID2)
        nextUID1 = self.posix_users._getUID()
        u = self.posix_users.addProperties(None, "UsEr1TesT", "", {"primaryGroup": "GrOUp1TesT"})
        self.assertEqual(str(u.uidNumber), nextUID1)
        self.assertEqual(str(u.gidNumber), nextGID1)
        self.assertEqual(str(u.gecos), "Test user 1 UsEr1TesT")
        nextUID2 = self.posix_users._getUID()
        u = self.posix_users.addProperties(None, "UsEr2TesT", "", {"primaryGroup": "GrOUp1TesT"})
        self.assertEqual(str(u.uidNumber), nextUID2)
        self.assertEqual(str(u.gidNumber), nextGID1)
        self.assertEqual(str(u.gecos), "Test user 2 Eau")
        u = self.posix_users.removeProperties(None, "UsEr2TesT")
        self.assertEqual(list(u.objectClass), [u'top', u'person', u'inetOrgPerson', u'organizationalPerson'])
        self.assertRaises(AttributeError, u.__getattr__, "uidNumber")

    def testChangePosixAttributes(self):
        self.users.addOne(None, "UsEr1TesT", "pasééù", {'givenName': 'Test user 1'})
        self.groups.addOne(None, "GrOUp1TesT", {'description': 'Test group 1'})
        self.groups.addOne(None, "GrOUp2TesT", {'description': 'Test group 2'})
        self.posix_users.addProperties(None, "UsEr1TesT", "", {"primaryGroup": "GrOUp1TesT"})
        self.posix_users.changeProperties(None, "UsEr1TesT", {"primaryGroup": "GrOUp2TesT"})
        u = self.posix_users.changeProperties(None, "UsEr1TesT", {"uidNumber": "20000"})
        self.assertEqual(str(u.uidNumber), "20000")
        self.assertEqual(str(u.gidNumber), "10001")

    def tearDown(self):
        self.groups.delete_r(self.groups_ou._dn)
        self.users.delete_r(self.users_ou._dn)


if __name__ == '__main__':
        unittest.main()
