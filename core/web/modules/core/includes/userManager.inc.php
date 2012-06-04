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

class UserProperty {

    public $name;
    public $label;
    public $current_value;
    public $default_value;
    public $new_value;

    private $modes = array('add', 'edit');
    private $template = array();
    private $container;

    function __construct($name, $label, $default_value = '') {
        $this->name = $name;
        $this->label = $label;
        $this->default_value = $default_value;
    }

    function getValue() {
        if ($this->new_value)
            return $this->new_value;
        else if ($this->current_value)
            return $this->current_value;
        else
            return $this->default_value;
    }

    function setTemplate($tpl, $mode = NULL) {
        if (in_array($mode, $this->modes)) {
            $this->template[$mode] = $tpl;
        }
        else {
            foreach($this->modes as $mode)
                $this->template[$mode] = $tpl;
        }
    }

    function getTemplate($mode = NULL) {
        if (!$mode)
            $mode = 'edit';
        return $this->template[$mode];
    }

    function setContainer($container = NULL) {
        if (!$container)
            $this->container = new TrFormElement();
        else
            $this->container = $container;
    }

    function renderValue() {
        $value = $this->getValue();
        if (is_array($value))
            return $value;
        else
            return array("value" => $value);
    }

    function renderContainer($mode) {
        if (!$this->template)
            throw new Error('Template not set.');

        $this->container->setDesc($this->label);
        $this->container->setTemplate($this->template[$mode]);

        return $this->container;
    }

    function render($formTable, $mode) {
        if (!$this->container)
            $this->setContainer();

        if (get_class($this->container) == "FormElement") {
            $formTable->pop();
            $formTable->add(
                $this->renderContainer($mode),
                $this->renderValue()
            );
            $formTable->push(new Table());
        }
        else {
            $formTable->add(
                $this->renderContainer($mode),
                $this->renderValue()
            );
        }

        return $formTable;
    }
}


class UserManager {

    public $name;
    public $has_groups;
    public $extensions;

    private $properties = array();
    private $properties_registered = false;

    private static $_instance = null;

    function __construct() {}

    function getInstance() {

        if (!isset($_SESSION["__INSTANCE_UM__"]) && is_null(self::$_instance)) {
            self::$_instance = new UserManager();
            self::$_instance->registerInstance();
        }
        else if (isset($_SESSION["__INSTANCE_UM__"])) {
            self::loadInstance();
        }

        return self::$_instance;
    }

    function loadInstance() {
        self::$_instance = unserialize($_SESSION["__INSTANCE_UM__"]);
    }

    function saveInstance() {
        //$_SESSION["__INSTANCE_UM__"] = serialize(self::$_instance);
    }

    function registerInstance() {
        $this->name = getUserManagerName();
        $this->has_groups = canUserHaveGroups();
        $this->extensions = getUserExtensionsList();
        $this->extensions = array_merge(array(array('general', $this->name)), $this->extensions);
        # Register all user properties
        foreach($this->extensions as $extension) {
            $name = $extension[0];
            $plugin = $extension[1];
            require_once('modules/'.$plugin.'/includes/userEdit'.ucfirst($name).'.inc.php');
        }
        $this->saveInstance();
    }

    function registerProperty($extension, $name, $label, $default_value = NULL) {
        $this->properties[$extension][$name] = new UserProperty($name, $label, $default_value);
    }

    function setPropertyTemplate($extension, $name, $tpl, $mode = NULL) {
        $this->properties[$extension][$name]->setTemplate($tpl, $mode);
    }

    function setPropertyContainer($extension, $name, $container = NULL) {
        $this->properties[$extension][$name]->setContainer($container);
    }

    function hasProperty($name) {
        foreach($this->extensions as $extension) {
            $extension_name = $extension[0];
            if (isset($this->properties[$extension_name]) && isset($this->properties[$extension_name][$name]))
                return $extension_name;
        }

        return false;
    }

    function getProperty($extension, $name) {
        if (isset($this->properties[$extension]) && isset($this->properties[$extension][$name]))
            return $this->properties[$extension][$name];
        else
            throw new Error("Property doesn't exists");
    }

    function getProperties($extension) {
        return $this->properties[$extension];
    }

}

class User {
    
    private $UM;

    function __construct($user) {
        $this->UM = UserManager::getInstance(); 
        // Load all known user properties
        foreach($this->UM->extensions as $extension) {
            $extension_name = $extension[0];
            $this->{$extension_name} = new stdClass;
            foreach($this->UM->getProperties($extension_name) as $prop_name => $prop) {
                $this->{$extension_name}->{$prop_name} = $prop;
            }
        }
    }

    function getProperties($extension) {
        return $this->{$extension};
    }

    function load($user) {
        // Load user values
        foreach($user as $prop => $value) {
            $extension = $this->UM->hasProperty($prop);
            if ($extension) {
                $this->{$extension}->{$prop}->current_value = $value;
                if (isset($this->{$extension}->{$prop.'_'}))
                    $this->{$extension}->{$prop.'_'}->current_value = $value;
            }
            else
                $this->{$prop} = $value;
        }

        if ($this->UM->has_groups && isset($this->general->groups)) {
            $all_groups = getGroups();
            $user_groups = array();
            if ($this->general->uid) {
                $res = getUserGroups($this->general->uid->current_value);
                foreach($res as $group) {
                    $user_groups[$group['cn']] = $group['cn'];
                }
            }
            $available_groups = array();
            foreach($all_groups[1] as $group) {
                if (!in_array($group['cn'], $user_groups))
                    $available_groups[$group['cn']] = $group['cn'];
            }

            $this->general->groups->current_value = array('member' => $user_groups,
                                                          'available' => $available_groups);
        }
    }

    function loadForm($values) {
        print_r($values);
        // Load the form values
        foreach($values as $prop => $value) {
            // Get changed values
            if ($values['old_' . $prop] != $value) {
                $extension = $this->UM->hasProperty($prop);
                if ($extension) {
                    $this->{$extension}->{$prop}->new_value = $value;
                }
            }
        }

        if ($this->UM->has_groups && $values['groups'] != $values['old_groups']) {
            $this->general->groups->new_value = array('member' => $values['groups'],
                                                      'available' => $values['available_groups']);
        }
    }

    function validate() {

    }

    function save() {

    }
}





?>
