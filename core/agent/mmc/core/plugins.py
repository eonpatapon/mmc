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
Manage MMC plugins
"""

import os
import imp
import sys
import logging
import glob
from mmc.support.mmctools import Singleton

log = logging.getLogger()

class PluginManager(Singleton):
    """
    This singleton class imports available MMC plugins, activates them, and
    keeps track of all enabled plugins.
    """

    pluginDirectory = 'plugins/'
    # Will contains the enabled plugins name and corresponding python
    # module objects
    plugins = {}

    def __init__(self):
        Singleton.__init__(self)

    def isEnabled(self, plugin):
        """
        @rtype: bool
        @return: Return True if the plugin has been enabled
        """
        return plugin in self.plugins

    def getEnabledPlugins(self):
        """
        @rtype: dict
        @return: the enabled plugins as a dict, key is the plugin name, value
                 is the python module object
        """
        return self.plugins

    def getEnabledPluginNames(self):
        """
        @rtype: list
        @return: the names of the enabled plugins
        """
        return self.getEnabledPlugins().keys()

    def getAvailablePlugins(self):
        """
        Fetch all available MMC plugin

        @param path: UNIX path where the plugins are located
        @type path: str

        @return: list of all .py in a path
        @rtype: list
        """
        ret = []
        for item in glob.glob(os.path.join(self.pluginDirectory, "*", "__init__.py")):
            ret.append(item.split("/")[1])
        return ret

    def loadPlugin(self, name, force=False):
        """
        Load a plugin with the given name.

        To start one single module after the agent startup, use startPlugin()
        instead

        @returns: 4 on fatal error (mmc agent should not start without that
        plugin), 0 on non-fatal failure, and the module itself if
        the load was successful
        """
        log.debug('Searching module %s' % name)
        f, p, d = imp.find_module(name, ['plugins'])

        try:
            log.debug("Trying to load module %s" % name)
            plugin = imp.load_module(name, f, p, d)
            log.debug("Module loaded: %s" % plugin)
        except Exception,e:
            log.exception(e)
            log.error('Plugin '+ name+ " raise an exception.\n"+ name+ " not loaded.")
            return 0

        # If module has no activate function
        try:
            # if not force:
            #     func = getattr(plugin, "activate")
            # else:
                # log.debug('Forcing plugin startup')
                # try:
            # func = getattr(plugin, "activateForced")
        # except AttributeError:
            # log.debug('Trying to force startup of plugin %s but no "activateForced" method found\nFalling back to the normale activate method' % (name,))
            func = getattr(plugin, "activate")
        except AttributeError:
            log.error('File %s is not a MMC plugin.' % name)
            plugin = None
            return 0

        # If is active
        try:
            if (func()):
                version = str(getattr(plugin, "getVersion")())
                log.info('Plugin %s loaded, version: %s' % (name, version))
            else:
                # If we can't activate it
                log.info('Plugin %s not loaded.' % name)
                plugin = None
        except Exception, e:
            log.error('Error while trying to load plugin %s' % name)
            log.exception(e)
            plugin = None
            # We do no exit but go on when another plugin than base fail

        # Check that "core" plugin was loaded
        if name == "core" and not plugin:
            log.error("MMC agent can't run without the core plugin. Exiting.")
            return 4
        return plugin

    def startPlugin(self, name):
        """
        Force a plugin load.
        Even if the configuration indicates the plugin is disabled,
        we load it and add it to the loaded list.

        Use it to start a plugin after the mmc agent startup, dynamically.

        This tries to call the activateForced method of the plugin (for example to
        ignore the disable = 1 configuration option)
        """
        if name in self.getEnabledPluginNames() or name in self.plugins:
            log.warning('Trying to start an already loaded plugin: %s' % (name,))
            return 0
        res = self.loadPlugin(name, force=True)
        if res == 0:
            return 0
        elif res is not None and not isinstance(res, int):
            self.plugins[name] = res
            # getattr(self.plugins["base"], "setModList")([name for name in self.plugins.keys()])
        elif res == 4:
            return 4
        return res

    def loadPlugins(self):
        """
        Find and load available MMC plugins

        @rtype: int
        @returns: exit code > 0 on error
        """
        # Find available plugins
        mod = {}
        sys.path.append("plugins")
        # self.modList = []
        plugins = self.getAvailablePlugins()

        if not "core" in plugins:
            log.error("Plugin 'core' is not available.")
            return 1
        else:
            # Set core plugin as the first plugin to load
            plugins.remove("core")
            plugins.insert(0, "core")

        # Put pulse2 plugins as the last to be imported, else we may get a mix
        # up with pulse2 module available in the main python path
        if "pulse2" in plugins:
            plugins.remove("pulse2")
            plugins.append("pulse2")

        # Load plugins
        log.info("Importing available MMC plugins")
        for plugin in plugins:
            res = self.loadPlugin(plugin)
            if res == 0:
                continue
            elif res is not None and not isinstance(res, int):
                mod[plugin] = res
            elif res == 4:
                return 4

        # store enabled plugins
        self.plugins = mod

        log.info("MMC plugins activation stage 2")
        for plugin in plugins:
            if self.isEnabled(plugin):
                try:
                    func = getattr(mod[plugin], "activate_2")
                except AttributeError:
                    func = None
                if func:
                    if not func():
                        log.error("Error in activation stage 2 for plugin '%s'" % plugin)
                        log.error("Please check your MMC agent configuration and log")
                        return 4

        # Set module list
        # getattr(self.plugins["base"], "setModList")([name for name in self.plugins.keys()])
        return 0

    def stopPlugin(self, name):
        """
        Stops a plugin.

        @rtype: boolean
        returns: True on success, False if the module is not loaded.
        """
        if not name in self.plugins:
            return False
        plugin = self.plugins[name]
        try:
            deactivate = getattr(plugin, 'deactivate')
        except AttributeError:
            log.info('Plugin %s has no deactivate function' % (name,))
        else:
            log.info('Deactivating plugin %s' % (name,))
            deactivate()
        del self.plugins[name]
        getattr(self.plugins["base"], "setModList")([name for name in self.plugins.keys()])
        return True

