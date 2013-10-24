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

import hyperkitty

def plugins_list():
    pass

class PluginRegistry():
    plugins = {}
    pluginsClass = {}
    urls = None
    templates_dirs = []
    thread_tabs = []
    message_templates = []
    thread_templates = []
    overview_templates = []
    thread_indexes = [    "thread_id","email_id_hashes", "subject", "participants", "length", "date_active",
             "category", 
                ]
    def __init__(self):
        self.urls = patterns('',url(r'plugins/','hyperkitty.lib.plugins.plugins_list'))
        print "instanciating plugin registry"
        #if pluginRegistry == None:
        #	pluginRegistry = self
        	
    def plugins_list(self):
        pass
    
    def register(self,name, pluginClass, attrs):
        if name not in self.pluginsClass:
            self.pluginsClass[name] = pluginClass
            print "registered " + name
            self.init_plugin(name)
        
    def get_urls(self):
        return self.urls
    #XXX handle some plugin conf
    # or may be plugin-dev driven
    def init_plugin(self,pluginClass):
        """
        Initialize plugin
        """
        
        # instanciate every registered plugin
        plugin = self.pluginsClass[pluginClass]()
        self.plugins[pluginClass] = plugin
        if 'templates_dir' in plugin.__dict__.keys():
            self.templates_dirs.append(plugin.templates_dir)
        try:
            print "configuring urls for plugin " + pluginClass
            if self.urls != None:
               self.urls += self.plugins[pluginClass].urls
            else:
                self.urls = self.plugins[pluginClass].urls
        except:
        	""
        if 'message_templates' in plugin.__dict__.keys():
            self.message_templates.extend(plugin.message_templates)
        if 'thread_template' in plugin.__dict__.keys():
            self.thread_templates.extend(plugin.thread_template)
        if 'overview_templates' in plugin.__dict__.keys():
            self.overview_templates.extend(plugin.overview_templates)
        if 'thread_indexes' in plugin.__dict__.keys():
            self.thread_indexes.extend(plugin.thread_indexes)
        if 'thread_tabs' in plugin.__dict__.keys():
            self.thread_tabs.append(plugin.thread_tabs)
                
    def thread_view(self,request,thread,context=None):
        """
        """
        print "assigning templates :" + repr(self.thread_templates) 
        if context != None and 'plugins_thread_templates' not in context.keys():
            context['plugins_thread_templates'] = self.thread_templates
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            try:
                plugin.thread_view(request,thread,context)
            except:
                pass
    
    def process_subscriptions(self,subscriptions,context):
        '''
        '''
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
            try :
                plugin.threads_overview(request,threads,context)
            except:
                ""


    def thread_index(self,request,thread,context):
    	"""
    	used in thread.thread_index view
    	Load plugins additional data for context
    	
    	populates tabs from plugins in the template thread.html
    	
    	tab plugin definition is an optional attribute of plugin object named thread_tabs
    	and containing an array with 2 members :
    	First : the tag label
    	Second : the tag ajax url on a defined destination
    	
    	"""
    	if context != None and 'plugins_thread_tabs' not in context:
            context['plugins_thread_tabs'] = self.thread_tabs
            print repr(self.thread_tabs)
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            try:
                plugin.thread_index(request,thread,context)
            except:
                ""
    
    def message_view(self,request,message,context=None):
        """
        Entry point for a single message view
        """
        if context != None and 'plugins_message_templates' not in context:
            context['plugins_message_templates'] = self.message_templates
        for pluginName in self.plugins.keys():
            plugin = self.plugins[pluginName]
            try:
                print "calling message_view of plugin %s" % pluginName
                plugin.message_view(request,message,context)
            except:
                print "calling of message_view for plugin %s failed" % pluginName
                
    def plugins_list():
        pass


hyperkitty.pluginRegistry = None
pluginRegistry = None
def getPluginRegistry():
    global pluginRegistry
    if hyperkitty.pluginRegistry == None:
        hyperkitty.pluginRegistry = PluginRegistry()
        pluginRegistry = hyperkitty.pluginRegistry
    return hyperkitty.pluginRegistry


class PluginMeta(type):
    """
    Plugin metaclass
    """
    def __init__(self, name, bases, attrs):
        super(PluginMeta, self).__init__(name, bases, attrs)
        if name != "IPlugin":
            print 'registering META ' + name
            getPluginRegistry().register(name, self,attrs)
            
    def __call__(cls, *args, **kwds):
        
        return type.__call__(cls, *args, **kwds)


class IPlugin():
    """Base Class for any plugin
    
    The class plugin may implement :
      - message_index : hook the message controller with (request,mlist,message)
    """
    __metaclass__ = PluginMeta

# Load external plugins

#for pluginModule in settings.HYPERKITTY_PLUGINS:
#    print 'loading module for ' + pluginModule
#    __import__(pluginModule)

    
    
