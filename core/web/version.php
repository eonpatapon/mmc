<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
?>
<?php

/* Display MMC architecture component versions */

require("includes/config.inc.php");

require("includes/acl.inc.php");
require("includes/session.inc.php");

includeInfoPackage(fetchModulesList($conf["global"]["rootfsmodules"]));

$modules = array();
foreach ($_SESSION["supportModList"] as $name) {
    $agent_version = xmlCall($name.".getVersion", null);
    if (in_array($name, $_SESSION["modulesList"]))
        $web_version = $__version[$name];
    else
        $web_version = false;
    $modules[$name] = array('agent' => $agent_version, 'web' => $web_version);
}

echo "<h1>" . _("MMC components version") . "</h1><br />
<strong>" . _("MMC agent: version") . "</strong> " . $_SESSION["modListVersion"]['ver'] . "<br />
<strong>" . _("core agent plugin: version") . "</strong> " . $modules['core']['agent'] . "<br /><br />";

foreach ($modules as $name => $versions) {
    if ($name != "core") {
        echo "<strong>$name " . _("plugin") . "</strong><br/>";
        echo _("agent: version") . " " . $versions['agent'] . "<br/>";
        if ($versions['web'])
            echo _("web: version") . " " . $versions['web'] . "<br/>"; 
        else
            echo '<div style="color : #D00;">' . _("web: plugin is not installed") . '</div>';
        echo "<br/>";
    }
}

?>
