<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
 *
 * Author: Alexandre Proença e-mail alexandre@mandriva.com.br
 * Date: 09/02/2012
 * Last Change: 11/20/2012
 * Description: This a page to render html elements and get user input, check the input and call action page or function
*/
?>
<?php
require("modules/squid/includes/config.inc.php");//global includes
require("modules/squid/includes/squid.inc.php"); //call squid-xmlrpc.inc.php (xml-rpc functions)
require("localSidebar.php");
require("graph/navbar.inc.php");

//Get list of the extension blocked from /etc/squid/rules/group_internet/normal_blacklist_ext.txt
$arrB = get_nonIndexExtList();


//New page with side menu, create and show
$p = new PageGenerator();
$p->setSideMenu($sidemenu);
$p->displaySideMenu();
$p->display();

//Create a list of informations
$n = new ListInfos($arrB,"List of extensions blocked");
$n->setName(_T("List"));
$n->setCssClass("squidExtlist");

//Create Title and show
$t = new TitleElement(_T("Extension Blocked Manager"), 2);
$t->display();

//Create Form to get informations
$f = new ValidatingForm();

//Create table inside Form
$f->push(new Table());

// Add new element input type
$f->add(new TrFormElement("<strong>" . _T("Extension to be blocked:") . "</strong>" , new InputTpl("extlistName" )), array("value" => ""));

//Add Botton in Form
$f->addButton("btnAdd", _T("Add"));
$f->display();

//Add action on list and show list
$n->addActionItem(new ActionPopupItem(_("Delete"),"deletex","delete","extlist") );
$n->display();

//Reder a button to reload squid service and put changes on
$f2 = new Form();
$f2->addButton("btnApply", _T("Apply"));
$f2->display();

//Check Add Botton
if (isset($_POST["btnAdd"])) {
	$extlistName = $_POST["extlistName"];
	if ((preg_match("/^[\?,\*,\#,\&,\(,\),]/", $extlistName))) {
		$n1 = new NotifyWidget();
		$n1->add(sprintf(_T("Invalid words %s insert names without special characters"), $extlistName));
		header("Location: " . urlStrRedirect("squid/normalgroup/extmanager"));
	} else  {
		$arrB = get_blacklist();
		addElementInExtList($extlistName, $arrB);
		if (!isXMLRPCError()) {
			header("Location: " . urlStrRedirect("squid/normalgroup/extmanager"));
		}
	}
}

//Check Apply Botton
if (isset($_POST["btnApply"])) {
	header("Location: " . urlStrRedirect("squid/normalgroup/restart"));

}
?>


