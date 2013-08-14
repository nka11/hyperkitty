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

from voting import set_message_votes, set_thread_votes
from django.conf.urls import patterns, include, url
from hyperkitty.lib import get_store
from models import Rating
from hyperkitty.lib.plugins import IPlugin
import os
templatesdir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates')


class VotePlugin(IPlugin):
    thread_indexes = ["likes", "dislikes", "likestatus"]
    def __init__(self):
        self.templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates')
        self.message_templates = ["vote/messages/like_form.html"]
        self.thread_templates = ["vote/threads/like.html"]
        self.overview_templates = ["vote/threads/overview.html"]
        self.profile_tab = "Votes"
        self.urls = patterns('hyperkitty.plugins.vote.views',
            url(r'^list/(?P<mlist_fqdn>[^/@]+@[^/@]+)/message/(?P<message_id_hash>\w+)/vote$',
                'message_vote', name='message_vote'),
            url(r'^accounts/profile/votes$', 'votes', name='user_votes'),
        )
    def message_view(self,request,message,context):
        set_message_votes(message, request.user)
    def thread_view(self,request,thread,context):
        set_thread_votes(thread,request.user)
    def threads_overview(self,request,threads,context):
        context['pop_threads'] = sorted([ t for t in threads if t.likes - t.dislikes > 0 ],
             key=lambda t: t.likes - t.dislikes,
             reverse=True)[:5]

