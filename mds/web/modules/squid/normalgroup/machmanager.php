<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
 *
 * Author: Alexandre Proença e-mail alexandre@mandriva.com.br
 * Date: 09/02/2012
 * Last Change: 11/20/2012
 * Description: This a page to render html elements and get user input, check the input and call action page or function
*/
?>
<?php
/* $Id$ */
require("modules/squid/includes/config.inc.php");//global includes
require("modules/squid/includes/squid.inc.php"); //call squid-xmlrpc.inc.php (xml-rpc functions) 
require("localSidebar.php");  
require("graph/navbar.inc.php");

//Get keywords and Domain list from /etc/squid/rules/group_internet/normal_whitelist.txt 
$arrB = get_nonIndexMachList();


//New page with side menu, create and show
$p = new PageGenerator();
$p->setSideMenu($sidemenu);
$p->displaySideMenu();
$p->display();

//Create a list of informations 
$n = new ListInfos($arrB,"List of IP address allowed");
$n->setName(_T("List"));

//Create Title and show
$t = new TitleElement(_T("Allow Machines"), 2);
$t->display();

//Create Form to get informations
$f = new ValidatingForm();

//Create table inside Form
$f->push(new Table()); 

// Add new element input type 
$f->add(new TrFormElement("<strong>" . _T("Enter IP Address to allow free access to Internet:") . "</strong>", new InputTpl("ipaddress" )), array("value" => ""));

//Add Botton in Form
$f->addButton("btnAdd", _T("Add"));
$f->display();

//Add action on list and show list
$n->addActionItem(new ActionPopupItem(_("Delete"),"deletem","delete","blacklist") );
$n->setCssClass("squidMachlist");

$n->display();

//Reder a button to reload squid service and put changes on
$f2 = new Form();
$f2->addButton("btnApply", _T("Apply"));
$f2->display();

//Check Add Botton
if (isset($_POST["btnAdd"])) {
	$ipaddress = $_POST["ipaddress"];
	if ((preg_match("/^[\?,\*,\#,\&,\(,\),]/", $ipaddress))) {
		$n1 = new NotifyWidget();
		$n1->add(sprintf(_T("Invalid words %s insert names without special characters"), $ipaddress));
		header("Location: " . urlStrRedirect("squid/normalgroup/machmanager"));
	} else  {
		$arrB = get_blacklist();
		addElementInMachList($ipaddress, $arrB);
		if (!isXMLRPCError()) {
			header("Location: " . urlStrRedirect("squid/normalgroup/machmanager"));
		}
	}
}

//Check Apply Botton
if (isset($_POST["btnApply"])) {
	header("Location: " . urlStrRedirect("squid/normalgroup/restart"));

}
?>


