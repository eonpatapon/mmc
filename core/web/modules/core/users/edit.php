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
require_once("includes/FormHandler.php");

switch($_GET["action"]) {
    case "add":
        $mode = "add";
        $title = _("Add user");
        $activeItem = "add";
        break;
    case "edit":
        $mode = "edit";
        $title = _("Edit user");
        $activeItem = "list";
        $uid = $_GET["user"];
        $user = getUser($uid);
        break;
    default:
        $mode = false;
        break;
}

$managerName = getUserManagerName();
// Get user attributes
require('modules/' . $managerName . '/includes/userForm.inc.php');

$p = new PageGenerator($title);
$sidemenu->forceActiveItem($activeItem);
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm(array('method' => 'post',
    'enctype' => 'multipart/form-data'));
// add submit button
$f->addValidateButton($mode);
$f->addCancelButton("reset");

$d = new DivForModule(_("User attributes"), "#F4F4F4");
$d->push(new Table());

foreach($attributes as $attr) {

    if (is_array($attr['widget']))
        $widget = $attr['widget'][$mode];
    else
        $widget = $attr['widget'];

    if (isset($attr['value']))
        $value = $attr['value'];
    else if (isset($user[$attr['name']]))
        $value = $user[$attr['name']];
    else
        $value = "";

    if (isset($attr['container']) && is_object($attr['container'])) {
        $container = $attr['container'];
        $container->setDesc($attr['label']);
        $container->setTemplate($widget);
        $d->pop();
        $d->add(
            $container,
            $value
        );
        $d->push(new Table());
    }
    else {
        $d->add(
            new TrFormElement($attr['label'], $widget),
            array("value" => $value)
        );
    }

}

$d->pop();

$f->push($d);
$f->display();

?>
