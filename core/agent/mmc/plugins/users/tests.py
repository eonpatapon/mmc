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

import unittest

from mmc.plugins.users import Users, PosixUsers, UserDoesNotExists, \
                              Groups

class TestUsersGroups(unittest.TestCase):

    def setUp(self):
        self.groups = Groups()
        self.groups_ou = self.groups.addOU("groups_test")
        self.groups.changeBase(self.groups_ou._dn)
        self.users = Users()
        self.posix_users = PosixUsers()
        self.users_ou = self.users.addOU("users_tests")
        self.users.changeBase(self.users_ou._dn)

    def testAddDelUser(self):
        u = self.users.addOne(None, "user", "pasééù", {'givenName': 'Test user'})
        self.assertEqual(str(u.uid), 'user')
        self.assertTrue(u.check_password('pasééù'))
        self.assertEqual(len(self.users.getAll(None)), 1)
        self.users.changeAttributes(None, 'user', {'mail': 'user@example.com'})
        # update our current object
        u.retrieve_attributes()
        self.assertEqual(str(u.mail), 'user@example.com')
        self.users.changeAttributes(None, 'user', {'preferredLanguage': 'fr;en', 'mobile': '+336456789' })
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
        g = self.groups.addOne("group", {'description': 'Test group', 
                                         'bad_attr': False })
        self.assertEqual(list(g.objectClass), [u'namedObject', u'posixGroup'])
        self.assertEqual(str(g.gidNumber), "10000")
        self.assertEqual(str(g.description), 'Test group')
        self.assertRaises(AttributeError, g.__getattr__, 'bad_attr')
        self.groups.removeOne('group')
        self.assertFalse(self.groups.check_if_dn_exists(g._dn))

    def testAddDelGroupUser(self):
        self.groups.addOne("group")
        self.users.addOne(None, "user", "pasééù", {'givenName': 'Test user'})
        g = self.groups.addUser("group", "user")
        self.assertEqual(list(g.objectClass), [u'groupOfNames', u'posixGroup'])
        self.assertEqual(str(g.memberUid), 'user')
        self.assertEqual(str(g.member), 'uid=user,ou=users_tests,ou=People,dc=mandriva,dc=com')
        g = self.groups.removeUser("group", "user")
        self.assertEqual(list(g.objectClass), [u'namedObject', u'posixGroup'])
        self.assertRaises(AttributeError, g.__getattr__, 'memberUid')
        self.assertRaises(AttributeError, g.__getattr__, 'member')

    def testAddWithNonExistantMember(self):
        self.groups.addOne("group", {'description': 'test group'})
        self.assertRaises(UserDoesNotExists, self.groups.addUser, "group", "user")

    def testRemoveUserFromAll(self):
        self.users.addOne(None, "user1", "pasééù", {'givenName': 'Test user 1'})
        self.users.addOne(None, "user2", "pasééù", {'givenName': 'Test user 2'})
        self.groups.addOne("group1", {'description': 'Test group 1 héhé'})
        self.groups.addUser("group1", "user1")
        g = self.groups.addUser("group1", "user2")
        self.assertEqual(list(g.member), [u'uid=user1,ou=users_tests,ou=People,dc=mandriva,dc=com', u'uid=user2,ou=users_tests,ou=People,dc=mandriva,dc=com'])
        self.assertEqual(list(g.memberUid), [u'user1', u'user2'])
        self.groups.addOne("group2", {'description': 'Test group 2'})
        self.groups.addUser("group2", "user1")
        self.groups.removeUserFromAll("user1")
        g = self.groups.getOne('group1')
        self.assertEqual(list(g.member), [u'uid=user2,ou=users_tests,ou=People,dc=mandriva,dc=com'])
        self.assertEqual(list(g.memberUid), [u'user2'])
        g = self.groups.getOne('group2')
        self.assertRaises(AttributeError, g.__getattr__, 'member')
        self.assertRaises(AttributeError, g.__getattr__, 'memberUid')

    def testGetuserGroups(self):
        self.users.addOne(None, "user1", "pasééù", {'givenName': 'Test user 1'})
        self.groups.addOne("group1", {'description': 'Test group 1'})
        self.groups.addOne("group2", {'description': 'Test group 1'})
        self.groups.addUser("group1", "user1")
        self.groups.addUser("group2", "user1")
        groups = self.users.getGroups(None, "user1")
        self.assertEqual(str(groups[0].cn), "group1")
        self.assertEqual(str(groups[1].cn), "group2")

    def testAddRemovePosixAttributes(self):
        self.users.addOne(None, "user1", "pasééù", {'givenName': 'Test user 1'})
        self.users.addOne(None, "user2", "pasééù", {'givenName': 'Test user 2', 'sn': "Éàù"})
        g = self.groups.addOne("group1", {'description': 'Test group 1'})
        self.assertEqual(str(g.gidNumber), "10000")
        g = self.groups.addOne("group2", {'description': 'Test group 2'})
        self.assertEqual(str(g.gidNumber), "10001")
        u = self.posix_users.addAttributes("user1", "", {"primaryGroup": "group1"})
        self.assertEqual(str(u.uidNumber), "10000")
        self.assertEqual(str(u.gidNumber), "10000")
        self.assertEqual(str(u.gecos), "Test user 1 user1")
        u = self.posix_users.addAttributes("user2", "", {"primaryGroup": "group1"})
        self.assertEqual(str(u.uidNumber), "10001")
        self.assertEqual(str(u.gidNumber), "10000")
        self.assertEqual(str(u.gecos), "Test user 2 Eau")
        u = self.posix_users.removeAttributes("user2")
        self.assertEqual(list(u.objectClass), [u'top', u'person', u'inetOrgPerson', u'lmcUserObject'])
        self.assertRaises(AttributeError, u.__getattr__, "uidNumber")

    def tearDown(self):
        self.groups.delete_r(self.groups_ou._dn)
        self.users.delete_r(self.users_ou._dn)


if __name__ == '__main__':
        unittest.main()
