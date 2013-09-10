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
from helpers import is_thread_unread
from hyperkitty.lib import get_store
from hyperkitty.models import LastView
from hyperkitty.lib.plugins import IPlugin
import os
templatesdir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates')


class LastViewPlugin(IPlugin):
    thread_indexes = []
    
    def __init__(self):
        """
        self.message_templates = ["vote/messages/like_form.html"]
        self.thread_templates = ["vote/threads/like.html"]
        self.overview_templates = ["vote/threads/overview.html"]
        self.profile_tab = "Votes"
        self.urls = patterns('hyperkitty.plugins.vote.views',
            url(r'^list/(?P<mlist_fqdn>[^/@]+@[^/@]+)/message/(?P<message_id_hash>\w+)/vote$',
                'message_vote', name='message_vote'),
            url(r'^accounts/profile/votes$', 'votes', name='user_votes'),
        )
        """
        self.templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates')
        self.thread_indexes = [ 'unread' ]
    def process_subscriptions(self,subscriptions,context):
        """
        """
    
    def message_view(self,request,message,context):
        """
        """
    
    def thread_index(self,request,thread,context={}):
        """
        """
        # Last view
        context['last_view'] = None
        if request.user.is_authenticated():
            last_view_obj, created = LastView.objects.get_or_create(
                    list_address=context['mlist_fqdn'], threadid=context['threadid'], user=request.user)
            if not created:
                context['last_view'] = last_view_obj.view_date
                last_view_obj.save() # update timestamp
        # get the number of unread messages
        if context['last_view'] is None:
            if request.user.is_authenticated():
                context['unread_count'] = len(thread)
            else:
                context['unread_count'] = 0
        else:
            # XXX: Storm-specific
            context['unread_count'] = thread.replies_after(context['last_view']).count()
    
    def thread_view(self,request,thread,context):
        """
        """
        thread.unread = is_thread_unread(request, thread)
        
    def threads_overview(self,request,threads,context):
        """"""
