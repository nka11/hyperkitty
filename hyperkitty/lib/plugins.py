#-*- coding: utf-8 -*-
# Copyright (C) 1998-2012 by the Free Software Foundation, Inc.
#
# This file is part of HyperKitty.
#
# HyperKitty is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# HyperKitty is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# HyperKitty.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Nicolas Karageuzian <nicolas@karageuzian.com>
#
from django.conf.urls import patterns, include, url
from django.conf import settings

class PluginRegistry():
    plugins = {}
    pluginsClass = {}
    urls = None
    message_index_hooks = []
    templates_dirs = []
    def __init__(self):
        self.urls = patterns('',url(r'plugins/','hyperkitty.lib.plugins.plugins_list'))
    def plugins_list(self):
        pass
    
    def register(self,name, pluginClass, attrs):
        self.pluginsClass[name] = pluginClass
        
    def get_urls(self):
        return self.urls
    #XXX handle some plugin conf
    # or may be plugin-dev driven
    def init_plugins(self):
        for pluginClass in self.pluginsClass.keys():
            # instanciate every registered plugin
            self.plugins[pluginClass] = self.pluginsClass[pluginClass]()
            if 'templates' in self.plugins[pluginClass].__dict__.keys():
                self.templates_dirs.append(self.plugins[pluginClass].templates)
            if 'urls' in self.plugins[pluginClass].__dict__.keys():
                if self.urls != None:
                   self.urls += self.plugins[pluginClass].urls
                else:
                    self.urls = self.plugins[pluginClass].urls
            
    def message_index(self,request,message,context=None):
        if context != None and 'plugins_templates' not in context:
            context['plugins_templates'] = []
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            if plugin.message_index :
                plugin.message_index(request,message)
            if context != None and "message_templates" in plugin.__dict__ and pluginName + "_message_index_templates" not in request.__dict__:
                request.__dict__[pluginName + "_message_index_templates"] = True
                context['plugins_templates'].extend(plugin.message_templates)
def plugins_list():
    pass

pluginRegistry = PluginRegistry()

class PluginMeta(type):
    """
    Plugin metaclass
    """
    def __init__(self, name, bases, attrs):
        super(PluginMeta, self).__init__(name, bases, attrs)
        if name != "IPlugin":
            pluginRegistry.register(name, self,attrs)
            
    def __call__(cls, *args, **kwds):
        
        return type.__call__(cls, *args, **kwds)


class IPlugin():
    """Base Class for any plugin
    
    The class plugin may implement :
      - message_index : hook the message controller with (request,mlist,message)
    """
    __metaclass__ = PluginMeta

# Load external plugins

for pluginModule in settings.HYPERKITTY_PLUGINS:
    __import__(pluginModule)

#Initialize all plugins
pluginRegistry.init_plugins()

    
    
