<?php

/**
 *  convert an aclString to an aclArray
 */
function createAclArray($aclString) {
    $acl = "";
    $aclattr = "";
    if (strpos($aclString, '/') === False) {
        $acl = $aclString;
    } else {
        list($acl, $aclattr) = split('/', $aclString);
    }

    $retacl = array();
    $retacltab = array();
    $retaclattr = array();

    /* get pages ACL */
    $arrayMod = split(':', $acl);
    foreach($arrayMod as $items) {
        if (substr_count($items, "#") == 2) {
            list($mod, $submod, $action) = split('#', $items);
            $retacl[$mod][$submod][$action]["right"] = "on";
        } else if (substr_count($items, "#") == 3) {
            list($mod, $submod, $action, $tab) = split('#', $items);
            $retacltab[$mod][$submod][$action][$tab]["right"] = "on";
        }
    }

    /* get attribute ACL */
    if (strlen($aclattr)) {
        $arrayAttr=split(':',$aclattr);
        foreach($arrayAttr as $items) {
            if (!empty($items)) {
                list($attrName,$value) = split('=',$items);
                $retaclattr[$attrName]=$value;
            }
        }
    }
    
    return array($retacl, $retacltab, $retaclattr);
}

/**
 * Set the current interface mode.
 * A cookie that expires in 30 days is used to keep user interface mode between
 * two MMC sessions.
 * 
 * @param $value 0 to set standard mode, 1 to set expert mode
 */
function setExpertMode($value) {
    global $conf;
    setcookie("expertMode", $value, time() + 3600 * 24 * 30, $conf["global"]["root"]);
}

/**
 * Returns 0 if the interface is in standard mode, or 1 if in expert mode.
 */
function isExpertMode() {
    $ret = 0;
    if (isset($_COOKIE["expertMode"]))
        $ret = $_COOKIE["expertMode"];
    return $ret;
}

function displayExpertCss() {
    if (isExpertMode()) {
        print ' style="display: inline;"';
    } else {
        print ' style="display: none;"';
    }
}

?>
