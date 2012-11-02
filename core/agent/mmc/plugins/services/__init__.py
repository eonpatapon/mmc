# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
MMC plugin for controlling systemd
"""

import logging

from mmc.plugins.services.manager import ServiceManager
from mmc.plugins.services.config import ServicesConfig

logger = logging.getLogger()

VERSION = "3.0.5"
APIVERSION = "0:1:0"
REVISION = ""

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    config = ServicesConfig("services")
    if config.disabled:
        logger.warning("Plugin services: disabled by configuration.")
        return False
    logger.debug("Loading systemd units")
    ServiceManager().list()
    try:
        from mmc.plugins.dashboard.manager import DashboardManager
        from mmc.plugins.services.panel import ServicesPanel
        DM = DashboardManager()
        DM.register_panel(ServicesPanel("services"))
    except ImportError:
        pass

    return True

# XML-RPC methods
def start(service):
    return ServiceManager().start(service)

def stop(service):
    return ServiceManager().stop(service)

def restart(service):
    return ServiceManager().restart(service)

def reload(service):
    return ServiceManager().reload(service)

def status(service):
    return ServiceManager().status(service)

def list():
    return ServiceManager().list()

def list_plugins_services():
    return ServiceManager().list_plugins_services()

def list_others_services(filter = None):
    return ServiceManager().list_others_services(filter)

def log(service = "", filter = ""):
    return ServiceManager().log(service, filter)
