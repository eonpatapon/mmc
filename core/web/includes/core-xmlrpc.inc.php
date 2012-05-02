<?php

function auth_user ($login, $pass)
{
    global $conf;
    global $error;

    if (($login == "") || ($pass == "")) return false;

    $param = array();
    $param[] = $login;
    $param[] = prepare_string($pass);

    $ret = xmlCall("core.authenticate",$param);
    if ($ret != "1") {
        if (!isXMLRPCError()) {
            $error = _("Invalid login");
        }
        return false;
    }

    /*$subscription = getSubscriptionInformation(true);
    if ($subscription['is_subsscribed']) {
        $msg = array();
        if ($subscription['too_much_users']) {
            $msg[] = _("users");
        }
        if ($subscription['too_much_computers']) {
            $msg[] = _("computers");
        }
        if (count($msg) > 0) {
            $warn = array(sprintf(_('WARNING: The number of registered %s is exceeding your license.'), implode($msg, ' and ')));
            $warn[] = _('Please contact your administrator for more information. If you are an administrator, please go to the license status page for more information.');

            new NotifyWidgetWarning(implode($warn, '<br/>'));
        }
    }*/

    return true;
}

?>
