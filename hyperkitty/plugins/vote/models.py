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

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Rating(models.Model):
    list_address = models.CharField(max_length=255, db_index=True)
    messageid = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User)
    vote = models.SmallIntegerField()

    def __unicode__(self):
        """Unicode representation"""
        if self.vote == 1:
            return u'%s liked message %s' % (unicode(self.user),
                    unicode(self.messageid))
        else:
            return u'%s disliked message %s' % (unicode(self.user),
                    unicode(self.messageid))

admin.site.register(Rating)
