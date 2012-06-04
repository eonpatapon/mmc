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


require("modules/core/includes/userManager.inc.php");

$UM =& UserManager::getInstance();

global $conf;

if(isset($_REQUEST['maxperpage']))
    $maxperpage = $_REQUEST['maxperpage'];
else
    $maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["filter"]))
    $filter = $_GET["filter"];
if (!$filter)
    $filter = "*";

if (isset($_GET["start"])) 
    $start = $_GET["start"];
else
    $start = NULL;

if (isset($_GET["end"])) 
    $end = $_GET["end"];
else
    $end = NULL;

$users = getUsers($filter, $start, $end);
$count = $users[0];
$users = $users[1];
$arrUser = array();
$arrExtra = array();

// Get attributes names
require('modules/' . $UM->name . '/includes/userList.inc.php');

foreach($users as $user) {
    $arrUser[] = $user[$login['attr']];
    foreach($extra as $key => $infos) {
        if (!isset($arrExtra[$key]))
            $arrExtra[$key] = array();

        $values = array();
        foreach($infos['value'] as $attr)
            $values[] = $user[$attr];

        if ($values)
            $arrExtra[$key][] = vsprintf($infos['pattern'], $values);
        else
            $arrExtra[$key][] = '';
    }
}

$n = new OptimizedListInfos($arrUser, $login['label']);
$n->setItemCount($count);
$n->setCssClass("userName");
$n->setNavBar(new AjaxPaginator(3, $filter, "updateSearchParam", $maxperpage));
$n->start = $start ? $start : 0;
$n->end = $count - 1;

foreach($arrExtra as $name => $values)
    $n->addExtraInfo($values, $name);

if ($actions['edit'])
    $n->addActionItem(new ActionItem(_("Edit"), "edit", "edit", "uid"));
if ($actions['acl'])
    $n->addActionItem(new ActionItem(_("MMC rights"), "editacl", "editacl", "uid"));
if ($actions['delete'])
    $n->addActionItem(new ActionPopupItem(_("Delete"), "delete", "delete", "uid"));
/*if (has_audit_working()) {
    $n->addActionItem(new ActionItem(_("Logged Actions"), "loguser", "audit", "user"));
}*/
$n->setName(_("Users"));
$n->display();

?>
