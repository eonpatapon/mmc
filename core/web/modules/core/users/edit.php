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

require("localSidebar.php");
require("graph/navbar.inc.php");
require("modules/core/includes/userManager.inc.php");

$UM = UserManager::getInstance();

switch($_GET["action"]) {
    case "add":
        $title = _("Add user");
        $activeItem = "add";
        $uid = '';
        break;
    case "edit":
        $title = _("Edit user");
        $activeItem = "list";
        $uid = $_GET["uid"];
        break;
    default:
        die();
}

$p = new TabbedPageGenerator();
$sidemenu->forceActiveItem($activeItem);
$p->setSideMenu($sidemenu);
$p->addTop($title);
foreach($UM->extensions as $extension) {
    $name = $extension[0];
    $plugin = $extension[1];
    $p->addTab($name, $name, "", "modules/core/users/editTabForm.php", array('uid' => $uid));
}
$p->addTab("acl", _("MMC ACLs"), "", "modules/core/users/acls.php", array('uid' => $uid));
$p->display();


?>
