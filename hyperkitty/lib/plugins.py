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

def plugins_list():
    pass

class PluginRegistry():
    plugins = {}
    pluginsClass = {}
    urls = None
    templates_dirs = []
    
    message_templates = []
    thread_templates = []
    overview_templates = []
    thread_indexes = [    "thread_id","email_id_hashes", "subject", "participants", "length", "date_active",
             "category", "unread",
                ]
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
        """
        Initialize plugins
        """
        for pluginClass in self.pluginsClass.keys():
            # instanciate every registered plugin
            plugin = self.pluginsClass[pluginClass]()
            self.plugins[pluginClass] = plugin
            if plugin.templates_dir:
                self.templates_dirs.append(plugin.templates_dir)
            if plugin.urls:
                if self.urls != None:
                   self.urls += self.plugins[pluginClass].urls
                else:
                    self.urls = self.plugins[pluginClass].urls
            if 'message_templates' in plugin.__dict__.keys():
                self.message_templates.extend(plugin.message_templates)
            if 'thread_templates' in plugin.__dict__.keys():
                self.thread_templates.extend(plugin.thread_templates)
            if 'overview_templates' in plugin.__dict__.keys():
                self.overview_templates.extend(plugin.overview_templates)
            if plugin.thread_indexes:
                self.thread_indexes.extend(plugin.thread_indexes)
                
    def thread_view(self,request,thread,context=None):
        """
        """
        if context != None and 'plugins_thread_templates' not in context.keys():
            context['plugins_thread_templates'] = self.thread_templates
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            if plugin.thread_view :
                plugin.thread_view(request,thread,context)
    def process_subscriptions(self,subscriptions,context):
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            if  plugin.process_subscriptions :
                plugin.process_subscriptions(subscriptions,context)
    def threads_overview(self,request,threads,context=None):
        """
        """
        if context != None and 'plugins_overview_templates' not in context.keys():
            context['plugins_overview_templates'] = self.overview_templates
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            if  plugin.threads_overview :
                plugin.threads_overview(request,threads,context)
    
    def message_view(self,request,message,context=None):
        """
        Entry point for a single message view
        """
        if context != None and 'plugins_message_templates' not in context:
            context['plugins_message_templates'] = self.message_templates
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            if plugin.message_view :
                plugin.message_view(request,message,context)
                
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
    print 'loading ' + pluginModule
    __import__(pluginModule)

#Initialize all plugins
pluginRegistry.init_plugins()

    
    
