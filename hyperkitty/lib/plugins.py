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

class PluginRegistry():
    plugins = {}
    pluginsClass = {}
    urls = None
    message_index_hooks = []
    
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
            if 'urls' in self.plugins[pluginClass].__dict__.keys():
                if self.urls != None:
                   self.urls += self.plugins[pluginClass].urls
                else:
                    self.urls = self.plugins[pluginClass].urls
            
    def message_index(self,request,mlist,message):
        for plugin in plugins:
            if "message_index" in plugin.__dict__:
                plugin.message_index(request,mlist,message)
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

# Load external plugins - raw hack for instance
#XXX Conf driven loading
import hyperkitty.plugins.vote

pluginRegistry.init_plugins()

    
    
