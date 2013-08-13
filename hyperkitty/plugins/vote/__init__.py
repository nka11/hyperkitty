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

from voting import set_message_votes
from django.conf.urls import patterns, include, url
from hyperkitty.lib import get_store
from models import Rating
from hyperkitty.lib.plugins import IPlugin
import os
templatesdir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates')


class VotePlugin(IPlugin):
    def __init__(self):
        self.templates = os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates')
        self.message_templates = ["messages/like_form.html"]
        self.profile_tab = "Votes"
        self.urls = patterns('hyperkitty.plugins.vote.views',
            url(r'^list/(?P<mlist_fqdn>[^/@]+@[^/@]+)/message/(?P<message_id_hash>\w+)/vote$',
                'message_vote', name='message_vote'),
            url(r'^accounts/profile/votes$', 'votes', name='user_votes'),
        )
    def message_index(self,request,message):
        set_message_votes(message, request.user)



