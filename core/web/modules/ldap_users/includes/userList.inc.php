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

// User login
$login = array(
    "label" => _T("Login", "ldap_users"),
    "attr" => 'uid'
);

// Extra info
$extra = array(
    _T("Name", "ldap_users") => 
        array('pattern' => '%s %s', 'value' => array('givenName', 'sn')), 
    _T("Mail") => 
        array('pattern' => '<a href="mailto:%s">%s</a>', 'value' => array('mail', 'mail')),
    _T("Phone") => 
        array('pattern' => '%s', 'value' => 'telephoneNumber')
);

$actions = array(
    "edit" => true,
    "delete" => true,
    "acl" => true
);

?>
