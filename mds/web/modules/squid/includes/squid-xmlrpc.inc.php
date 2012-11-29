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
?>
<?php

function get_blacklist()
{
    return xmlCall("squid.getNormalBlacklist",null);
}

function get_whitelist()
{
    return xmlCall("squid.getNormalWhitelist",null);
}

function get_extlist()
{
    return xmlCall("squid.getNormalExtlist",null);
}

function get_timelist()
{
    return xmlCall("squid.getNormalTimelist",null);
}

function get_machlist()
{
    return xmlCall("squid.getNormalMachlist",null);
}

function get_nonIndexBlackList() {
    $arrB =get_blacklist();
    sort($arrB);
    return $arrB;
}

function get_nonIndexWhiteList() {
    $arrW =get_whitelist();
    sort($arrW);
    return $arrW;
}

function get_nonIndexExtList() {
    $arrX =get_extlist();
    sort($arrX);
    return $arrX;
}

function get_nonIndexTimeList() {
    $arrT =get_timelist();
    sort($arrT);
    return $arrT;
}

function get_nonIndexMachList() {
    $arrM =get_Machlist();
    sort($arrM);
    return $arrM;
}

///////////////ADD/////////////////////////////////

function addElementInBlackList($element,&$arrBlackList) {
    xmlCall("squid.addNormalBlacklist",$element);
}

function addElementInWhiteList($element,&$arrWhiteList) {
    xmlCall("squid.addNormalWhitelist",$element);
}

function addElementInExtList($element,&$arrExtList) {
    xmlCall("squid.addNormalExtlist",$element);
}

function addElementInTimeList($element,&$arrTimeList) {
    xmlCall("squid.addNormalTimelist",$element);
}

function addElementInMachList($element,&$arrMachList) {
    xmlCall("squid.addNormalMachlist",$element);
}


//////////// DEL///////////////////////////////////

function delElementInBlackList($element,&$arrBlackList) {
    xmlCall("squid.delNormalBlacklist",$element);
}

function delElementInWhiteList($element,&$arrWhiteList) {
    xmlCall("squid.delNormalWhitelist",$element);
}

function delElementInExtList($element,&$arrExtList) {
    xmlCall("squid.delNormalExtlist",$element);
}

function delElementInTimeList($element,&$arrTimeList) {
    xmlCall("squid.delNormalTimelist",$element);
}

function delElementInMachList($element,&$arrMachList) {
    xmlCall("squid.delNormalMachlist",$element);
}


//////// ACTIONS ///////////////

function reloadService(){
    return xmlCall("squid.reloadSquid",null);
}

function startService(){
    return xmlCall("squid.startSquid",null);
}

function stopService(){
    return xmlCall("squid.stopSquid",null);
}

function getStatutProxy() {
    return xmlCall("squid.getStatutProxy",null);
}

function genSarg(){
    return xmlCall("squid.genSarg",null);
}

function cleanSarg(){
    return xmlCall("squid.cleanSarg",null);
}

?>
