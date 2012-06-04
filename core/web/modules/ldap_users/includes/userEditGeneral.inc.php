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

require("includes/languages.php");

$name = 'general';
$phoneregexp = "/^[a-zA-Z0-9(/ +\-]*$/";

$UM = UserManager::getInstance();

$UM->registerProperty($name, 'uid', _T("Login", "ldap_users"));
$UM->setPropertyTemplate($name, 'uid', new InputTpl("uid", '/^[a-zA-Z0-9][A-Za-z0-9_.\-]*$/'), 'add');
$UM->setPropertyTemplate($name, 'uid', new HiddenTpl("uid"), 'edit');

$UM->registerProperty($name, 'pass', _T("Password", "ldap_users"));
$UM->setPropertyTemplate($name, 'pass', new PasswordTpl("pass"));

$UM->registerProperty($name, 'confpass', _T("Confirm password", "ldap_users"));
$UM->setPropertyTemplate($name, 'confpass', new PasswordTpl("confpass"));

$UM->registerProperty($name, 'jpegPhoto', _T("Photo", "ldap_users"));
$UM->setPropertyTemplate($name, 'jpegPhoto', new ImageTpl("jpegPhoto"));

$UM->registerProperty($name, 'sn', _T("Last Name", "ldap_users"));
$UM->setPropertyTemplate($name, 'sn', new InputTpl("sn"));

$UM->registerProperty($name, 'givenName', _T("First Name", "ldap_users"));
$UM->setPropertyTemplate($name, 'givenName', new InputTpl("givenName"));

$UM->registerProperty($name, 'title', _T("Title", "ldap_users"));
$UM->setPropertyTemplate($name, 'title', new InputTpl("title"));

$UM->registerProperty($name, 'mail', _T("Mail", "ldap_users"));
$UM->setPropertyTemplate($name, 'mail', new MailInputTpl("mail"));

$UM->registerProperty($name, 'telephoneNumber', _T("Telephone number", "ldap_users"), array(''));
$UM->setPropertyTemplate($name, 'telephoneNumber', new MultipleInputTpl("telephoneNumber", _T("Telephone number", "ldap_users"), $phoneregexp));
$UM->setPropertyContainer($name, 'telephoneNumber', new FormElement());

$UM->registerProperty($name, 'mobile', _T("Mobile number", "ldap_users"));
$UM->setPropertyTemplate($name, 'mobile', new InputTpl("mobile", $phoneregexp));

$UM->registerProperty($name, 'facsimileTelephoneNumber', _T("Fax number", "ldap_users"));
$UM->setPropertyTemplate($name, 'facsimileTelephoneNumber', new InputTpl("facsimileTelephoneNumber", $phoneregexp));

$UM->registerProperty($name, 'homePhone', _T("Home phone number", "ldap_users"));
$UM->setPropertyTemplate($name, 'homePhone', new InputTpl("homePhone", $phoneregexp));

$languagesTpl = new SelectItem("preferredLanguage");
$labels = array(_("Choose language")) + array_values(getLanguages());
$values = array("") + array_keys(getLanguages());
$languagesTpl->setElements($labels);
$languagesTpl->setElementsVal($values);

$UM->registerProperty($name, 'preferredLanguage', _T("Preferred language", "ldap_users"));
$UM->setPropertyTemplate($name, 'preferredLanguage', $languagesTpl);

$groupsTpl = new MembersTpl('groups'); 
$groupsTpl->setTitle(_T("User's groups", "ldap_users"), _T("All groups", "ldap_users"));

$UM->registerProperty($name, 'groups', _T("Groups", "ldap_users"));
$UM->setPropertyTemplate($name, 'groups', $groupsTpl);

?>
