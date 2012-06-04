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


function getUserManagerName() {
    return xmlCall("core.getUserManagerName");
}

function getUserExtensionsList() {
    return xmlCall("core.getUserExtensionsList");
}

function canUserHaveGroups() {
    return xmlCall("core.canUserHaveGroups");
}

function hasUserExtension($extension, $uid) {
    return xmlCall("core.hasUserExtension", array($extension, $uid));
}

function getUsers($search = "*", $start = NULL, $end = NULL, $base = NULL) {
    return xmlCall("core.getUsers", array($search, $start, $end, $base));
}

function getUser($uid) {
    return xmlCall("core.getUser", array($uid));
}

function getUserGroups($uid) {
    return xmlCall("core.getUserGroups", array($uid));
}

function removeUser($uid) {
    return xmlCall("core.removeUser", array($uid));
}

function getGroups($search = "*", $start = NULL, $end = NULL, $base = NULL) {
    return xmlCall("core.getGroups", array($search, $start, $end, $base));
}

?>
