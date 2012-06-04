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

$name = 'posix';

$UM = UserManager::getInstance();

$posix_groups = getGroups("posixGroup");
$groups = $values = array();
foreach($posix_groups[1] as $group) {
    $groups[] = $group['cn'];
    $values[] = $group['gidNumber'];
}
$gidNumberTpl = new SelectItem("gidNumber");
$gidNumberTpl->setElements($groups);
$gidNumberTpl->setElementsVal($values);

$UM->registerProperty($name, 'gidNumber', _T("Primary group", "ldap_users"));
$UM->setPropertyTemplate($name, 'gidNumber', $gidNumberTpl);

$UM->registerProperty($name, 'homeDirectory', _T("Home directory", "ldap_users"));
$UM->setPropertyTemplate($name, 'homeDirectory', new InputTpl("homeDirectory"));

$UM->registerProperty($name, 'loginShell', _T("Login shell", "ldap_users"));
$UM->setPropertyTemplate($name, 'loginShell', new InputTpl("loginShell"));

$UM->registerProperty($name, 'gidNumber_', _T("GID", "ldap_users"));
$UM->setPropertyTemplate($name, 'gidNumber_', new HiddenTpl("gidNumber"));

$UM->registerProperty($name, 'uidNumber', _T("UID", "ldap_users"));
$UM->setPropertyTemplate($name, 'uidNumber', new HiddenTpl("uidNumber"));

?>
