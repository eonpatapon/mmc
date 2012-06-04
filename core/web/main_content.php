
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

/* bord haut gauche arrondi */
$topLeft = 1;

global $acl_error;

if ($acl_error) {
  print "<div id=\"errorCode\">$acl_error</div>";
}

function display_page($page,$submod,$mod) {
    if ($page->getDescription() && $page->isVisible()) {
        $url = urlStr($mod->getName()."/".$submod->getName()."/".$page->_action);
        if (hasCorrectAcl($mod->getName(),$submod->getName(),$page->_action)) {
            echo "<li><a href=\"$url\">".$page->getDescription()."</a></li>";
        } else {
            echo "<li style=\"color: #BBB;\">".$page->getDescription()."</li>";
        }
    }
}

function display_submod($submod,$mod) {
    if (!$submod->hasVisible()) {
        return;
    }
    echo '<div class="submod">';
    ?> <img src="<?php echo  $submod->_img ?>_select.png" alt="" style="float:right;" /><?php
    /*if (!$submod->_visibility) { //if submod not visible
        return;
    }*/
    echo '<h3>';
    $url = urlStr($submod->_defaultpage);
    echo "<a style=\"text-decoration: none;\" href=\"$url\">".$submod->getDescription()."</a><br/>";
    echo "</h3>";
    print "<ul>";
    foreach ($submod->getPages() as $page) {
        display_page($page,$submod,$mod);
    }
    print "</ul>";
    echo '</div>';
}

function display_mod($mod) {
    if (!$mod->hasVisible()) {
        return;
    }

?>
    <div class="module" id="<?php echo $mod->getName(); ?>">
        <h3 class="handle"><?php echo $mod->getDescription(); ?></h3>
        <?php foreach (getSorted($mod->getSubmodules()) as $submod) {
            display_submod($submod,$mod);
        }
        ?>
    </div>
<?php
}

$MMCApp =& MMCApp::getInstance();
$modules = getSorted($MMCApp->getModules());
$nb_modules = count($modules);

/* inclusion header HTML */
require("graph/navbar.inc.php");

?>

<style type="text/css">
<!--

#section, #sectionTopRight, #sectionBottomLeft { margin: 0 0 0 17px; }
#sectionTopRight { border-left: none; }
#sectionTopLeft {
    height: 9px;
    padding: 0;
    margin: 0;
    background: url("<?php echo $root; ?>img/common/sectionTopLeft.gif") no-repeat top left transparent;
}

.module {
    float: left;
    background-color: #EEE;
    padding: 5px;
    margin: 5px;
    margin-bottom: 10px;
    width: 180px;
    -moz-border-radius: 10px;
    -webkit-border-radius: 10px;
}

.submod {
    background-color: #E5E5E5;
    padding: 5px;
    margin: 10px;
    -moz-border-radius: 5px;
    -webkit-border-radius: 5px;
}

ul {
    margin: 0.5em;
    padding: 0.5em;
}

#home .home-column {
    float: left;
    width: 200px;
    border: 1px solid white;
    background: white;
    min-height: 100px;
    -moz-border-radius: 10px;
    -webkit-border-radius: 10px;
    margin-right: 5px;
    margin-bottom: 5px;
}

#home .module .handle {
    cursor: move;
}

-->
</style>
    <h2><?php echo  _("Home") ?></h2>
    <div id="home">
        <?php
        foreach($modules as $key => $mod) {
            display_mod($mod);
        }
        ?>
    </div>
    <div style="clear: both;"></div>
</div>

<script src="jsframework/cookiejar.js"></script>
<script type="text/javascript">

    Event.observe(window, 'load', function() {

        load = function() {
            try {
                settings = mmcookie.get('home-settings');
                saved_modules = 0;
                for(zone in settings)
                    for(module in settings[zone])
                        saved_modules++;
                // if there is more or less modules loaded
                // invalidate the settings
                if (modules.length != saved_modules)
                    settings = false;
            }
            catch (err) {
                mmcookie.remove('home-settings');
                settings = false;
            }
            if (!settings) {
                // create default settings
                settings = {};
                // store column info
                for(var c=0; c<cols; c++)
                    settings['home-column_'+c] = {};
                // add each module in a column
                for(var m=0, c=0; m<modules.length; m++, c++) {
                    settings['home-column_'+c][modules[m].id] = modules[m].id;
                    // don't fill the first column
                    // base module can be very high
                    if (c == cols-1)
                        c = 0;
                }
                // save the settings
                mmcookie.put('home-settings', settings);
            }
            // apply the settings
            zone_no = 0;
            for(zone in settings) {
                // create che columns
                var z = new Element('div', {'class': 'home-column', 'id': 'home-column_'+zone_no});
                // add modules in columns
                for(module in settings[zone])
                    z.appendChild(modules.find(function(m) { return m.id == module; }));
                // display the column
                home.appendChild(z);
                zone_no++;
            }
            // add more columns if needed
            if(Object.keys(settings).length < cols) {
                for(var i=Object.keys(settings).length; i<cols; i++) {
                    var z = new Element('div', {'class': 'home-column', 'id': 'home-column_'+i});
                    home.appendChild(z);
                }
            }
        }

        save = function() {
            new_settings = {};
            sortables.each(function (z) {
                $$('#'+z.id+' .module').each(function(m) {
                    if (!new_settings[z.id])
                        new_settings[z.id] = {};
                    new_settings[z.id][m.id] = m.id;
                });
            });
            mmcookie.put('home-settings', new_settings);
        }

        var settings = false;
        var mmcookie = new CookieJar({
            expires: 604800, // one week
            path: '/mmc/'
        });
        var home = $('home');
        var modules = $$('.module');
        // calculate the number of columns for the screen
        var cols = Math.floor($('home').offsetWidth / 210);
        // load the modules in the columns
        load();
        // make the modules sortable
        var sortables = $$('.home-column');
        sortables.each(function (sortable) {
          Sortable.create(sortable, {
            containment: sortables,
            constraint: false,
            tag: 'div',
            only: 'module',
            dropOnEmpty: true,
            handle: 'handle',
            hoverclass: 'module-hover'
          });
          $$('.handle').each(function(m) {
            m.observe("mousedown", function(m) {
                sortables.each(function (s) {
                    s.style.border = "1px solid #ccc";
                    s.style.background = "#FFFAFA";
                });
            });
          });
          $$('.handle').each(function(m) {
            m.observe("mouseup", function(m) {
                save();
                sortables.each(function (s) {
                    s.style.border = "1px solid white";
                    s.style.background = "white";
                });
            });
          });
        });
    });
</script>
