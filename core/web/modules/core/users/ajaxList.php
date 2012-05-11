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

global $conf;

if(isset($_REQUEST['maxperpage']))
    $maxperpage = $_REQUEST['maxperpage'];
else
    $maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["filter"]))
    $filter = $_GET["filter"];
if (!$filter)
    $filter = "*";

$users = getUsers($filter);
$arrUser = array();

foreach($users as $user) {
    $arrUser[] = $user['uid'];
}

print_r($arrUser);

$n = new UserInfos($arrUser, _("Login"));
$n->setItemCount(3);
$n->setNavBar(new AjaxPaginator(3, $filter, "updateSearchParam", $maxperpage));

$n->start = 0;
$n->end = 3 - 1;

/*$n->addExtraInfo($arrSnUser,_("Name"));
$n->addExtraInfo($mails,_("Mail"));
$n->addExtraInfo($phones,_("Telephone"));*/

$n->addActionItem(new ActionItem(_("Edit"), "edit", "edit", "user"));
$n->addActionItem(new ActionItem(_("MMC rights"), "editacl", "editacl", "user"));
$n->addActionItem(new ActionPopupItem(_("Delete"), "delete", "delete", "user"));
$n->addActionItem(new ActionPopupItem(_("Backup"), "backup", "backup", "user"));
/*if (has_audit_working()) {
    $n->addActionItem(new ActionItem(_("Logged Actions"), "loguser", "audit", "user"));
}*/
$n->setName(_("Users"));
$n->display();

?>
