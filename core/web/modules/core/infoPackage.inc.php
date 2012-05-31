<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
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

#require_once("modules/base/includes/computers.inc.php");
#require_once("modules/base/includes/logging-xmlrpc.inc.php");
require_once("modules/core/includes/users-xmlrpc.inc.php");

/**
 * module declaration
 */
$mod = new Module("core");
$mod->setVersion("3.0.3.2");
$mod->setRevision('$Rev$');
$mod->setAPIVersion("9:0:5");
$mod->setDescription(_("User and group management"));
$mod->setPriority(1);

/**
 * define main submod
 */

$submod = new SubModule("main", _("Home page"));
$submod->setVisibility(False);

$page = new Page("default",_("Home page"));
$page->setFile("main_content.php");
$page->setOptions(array("visible"=>False));
$submod->addPage($page);
$mod->addSubmod($submod);

/**
 * user submod definition
 */

$submod = new SubModule("users", _("Users"));
$submod->setImg('img/navbar/user');
$submod->setDefaultPage("core/users/list");
$submod->setPriority(10);

$page = new Page("list", _("User list"));
$submod->addPage($page);

$page = new Page("ajaxAutocompleteGroup");
$page->setFile("modules/core/users/ajaxAutocompleteGroup.php",
               array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxList");
$page->setFile("modules/core/users/ajaxList.php",
               array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("add",_("Add a user"));
$submod->addPage($page);

$page = new Page("edit",_("Edit a user"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("editacl",_("Edit ACL permissions on a user"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("loguser",_("Logged user actions"));
$page->setFile("modules/core/users/loguser.php",
	               array("AJAX" =>False,"visible"=>False));
$submod->addPage($page);

$page = new Page("logview",_("Action details"));
$page->setFile("modules/core/users/logview.php",
                   array("AJAX" =>False,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxLogFilter");
$page->setFile("modules/core/audit/ajaxLogFilter.php",
	               array("AJAX" =>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("delete",_("Delete a user"));
$page->setFile("modules/core/users/delete.php",
               array("noHeader" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("passwd",_("Change user password"));
if ($_SESSION["login"]=='root') {
    $page->setOptions(array("visible"=>False));
}
$submod->addPage($page);

$page = new Page("getPhoto", _("Get user photo"));
$page->setOptions(array("visible"=>False, "noHeader" =>True));
$submod->addPage($page);

$mod->addSubmod($submod);

/**
 * groups submod definition
 */

$submod = new SubModule("groups", _("Groups"));
$submod->setImg('img/navbar/group');
$submod->setDefaultPage("core/groups/index");
$submod->setPriority(20);

$page = new Page("index",_("Group list"));
$submod->addPage($page);

$page = new Page("add",_("Add a group"));
$submod->addPage($page);

$page = new Page("delete",_("Delete a group"));
$page->setFile("modules/core/groups/delete.php",
               array("noHeader"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("ajaxFilter");
$page->setFile("modules/core/groups/ajaxFilter.php",
               array("AJAX"=>True,"visible"=>False));
$submod->addPage($page);

$page = new Page("members",_("Group members"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$page = new Page("edit",_("Edit a group"));
$page->setOptions(array("visible"=>False));
$submod->addPage($page);

$mod->addSubmod($submod);


$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($mod);

?>
