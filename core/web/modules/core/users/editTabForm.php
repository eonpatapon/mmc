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

$UM = UserManager::getInstance();
$user = new User();

if (!isset($_GET['tab']))
    $extension = "general";
else
    $extension = $_GET['tab'];

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
        $uid = $_GET["uid"];
        $user->load(getUser($uid));
        break;
    default:
        $mode = false;
        break;
}

if (isset($_POST['edit']))
    $user->loadForm($_POST);
    if ($user->validate())
        $user->save();

$f = new ValidatingForm(array('method' => 'post',
    'enctype' => 'multipart/form-data'));
// add submit button
$f->addValidateButton($mode);
$f->addCancelButton("reset");

$f->push(new Table());

if ($extension != "general") {
    $state = hasUserExtension($extension, $uid);
    $f->add(
        new TrFormElement(_("Enable"), new CheckboxTpl($extension.'ext')),
        array("value" => $state ? "checked": "", "extraArg" => 'onclick="toggleVisibility(\''.$extension.'_div\');"')
    );
    $f->pop();
    $d = new Div(array("id" => $extension.'_div'));
    $d->setVisibility($state);
    $f->push($d);
    $f->push(new Table());
}

foreach($user->getProperties($extension) as $prop) {
    $f = $prop->render($f, $mode);
}

if ($extension != "general")
    $f->pop();
$f->pop();
$f->display();

?>
