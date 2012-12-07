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
 */

require("modules/squid/includes/squid.inc.php");
require("modules/squid/includes/config.inc.php");

if (isset($_POST["bdelblacklist"])) {
    $arrB=get_blacklist();
    delElementInBlackList($_POST["blacklist"],$arrB);
}
if (isset($_GET["blacklist"])) {
    $blacklist = urldecode($_GET["blacklist"]);

?>
	<form action="<?php echo urlStr("squid/normalgroup/delete"); ?>" method="post">
		<p><?php printf(_T("You will remove  <b>%s</b>"), $blacklist); ?></p>
		<br>
		<p><?php echo  _T("Are you sure ?"); ?></p>
		<input name="blacklist" type="hidden" value="<?php echo $blacklist; ?>" />
		<input name="bdelblacklist" type="submit" class="btnPrimary" value="<?php echo  _("Delete"); ?> <?php echo $blacklist; ?>" />
	<input name="bback" type="submit" class="btnSecondary" value="<?php echo  _("Cancel"); ?>" onclick="new Effect.Fade('popup'); return false;" />
	</form>
<?php
}
else if (isset($_POST["bdelblacklist"]))
{
    redirectTo(urlStrRedirect('squid/normalgroup/blackmanager'));
}
?>
