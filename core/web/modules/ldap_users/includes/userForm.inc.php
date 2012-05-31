<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

$attributes = array(
    array(
        'name' => 'uid',
        'label' => _T("Login", "ldap_users"),
        'widget' => array('add' => new InputTpl("uid", '/^[a-zA-Z0-9][A-Za-z0-9_.\-]*$/'),
                          'edit' => new HiddenTpl("uid")),
    ),
    array(
        'name' => 'pass',
        'label' => _T("Password", "ldap_users"),
        'widget' => new PasswordTpl("pass"),
        'value' => ''
    ),
    array(
        'name' => 'confpass',
        'label' => _T("Confirm password", "ldap_users"),
        'widget' => new PasswordTpl("confpass"),
        'value' => ''
    ),
    array(
        'name' => 'sn',
        'label' => _T("Last Name", "ldap_users"),
        'widget' => new InputTpl("sn")
    ),
    array(
        'name' => 'givenName',
        'label' => _T("First Name", "ldap_users"),
        'widget' => new InputTpl("givenName")
    ),
    array(
        'name' => 'title',
        'label' => _T("Title", "ldap_users"),
        'widget' => new InputTpl("title")
    ),
    array(
        'name' => 'mail',
        'label' => _T("Mail", "ldap_users"),
        'widget' => new MailInputTpl("mail")
    ),
    array(
        'name' => 'telephoneNumber',
        'label' => _T("Telephone number", "ldap_users"),
        'container' => new FormElement(),
        'widget' => new MultipleInputTpl("telephoneNumber", _T("Telephone number", "ldap_users"), "/^[a-zA-Z0-9(/ +\-]*$/"),
        'value' => array('')
    )
);
