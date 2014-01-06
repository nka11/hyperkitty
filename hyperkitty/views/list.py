# -*- coding: utf-8 -*-
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
# Author: Aamir Khan <syst3m.w0rm@gmail.com>
# Author: Aurelien Bompard <abompard@fedoraproject.org>
#

import datetime
from collections import namedtuple, defaultdict

import django.utils.simplejson as json
from django.shortcuts import redirect, render
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import formats
from django.utils.dateformat import format as date_format
from django.utils.timezone import utc
from django.http import Http404, HttpResponse

from hyperkitty.models import Tag, Favorite
from hyperkitty.lib import get_store
from hyperkitty.lib.plugins import pluginRegistry
from hyperkitty.lib.view_helpers import FLASH_MESSAGES, \
        get_category_widget, get_months, get_display_dates, daterange, \
        is_thread_unread, get_recent_list_activity
from hyperkitty.lib.paginator import paginate
from hyperkitty.lib.mailman import check_mlist_private


if settings.USE_MOCKUPS:
    from hyperkitty.lib.mockup import generate_top_author, generate_thread_per_category



@check_mlist_private
def archives(request, mlist_fqdn, year=None, month=None, day=None):
    if year is None and month is None:
        today = datetime.date.today()
        return redirect(reverse(
                'archives_with_month', kwargs={
                    "mlist_fqdn": mlist_fqdn,
                    'year': today.year,
                    'month': today.month}))

    begin_date, end_date = get_display_dates(year, month, day)
    store = get_store(request)
    mlist = store.get_list(mlist_fqdn)
    threads = store.get_threads(mlist_fqdn, start=begin_date, end=end_date)
    if day is None:
        list_title = date_format(begin_date, "F Y")
        no_results_text = "for this month"
    else:
        #list_title = date_format(begin_date, settings.DATE_FORMAT)
        list_title = formats.date_format(begin_date) # works with i18n
        no_results_text = "for this day"
    extra_context = {
        'month': begin_date,
        'month_num': begin_date.month,
        "list_title": list_title.capitalize(),
        "no_results_text": no_results_text,
    }
    if day is None:
        month_activity = mlist.get_month_activity(int(year), int(month))
        extra_context["participants"] = month_activity.participants_count
    return _thread_list(request, mlist, threads, extra_context=extra_context)


def _thread_list(request, mlist, threads, template_name='thread_list.html', extra_context={}):
    if mlist is None:
        raise Http404("No archived mailing-list by that name.")
    store = get_store(request)

    threads = paginate(threads, request.GET.get('page'))

    participants = set()
    for thread in threads:
        if "participants" not in extra_context:
            participants.update(thread.participants)

        # Plugins
        pluginRegistry.thread_view(request, thread, extra_context)

        # Favorites XXX to plugin

        thread.favorite = False
        if request.user.is_authenticated():
            try:
                Favorite.objects.get(list_address=mlist.name,
                                     threadid=thread.thread_id,
                                     user=request.user)
            except Favorite.DoesNotExist:
                pass
            else:
                thread.favorite = True

        # Tags XXX to plugin
        try:
            thread.tags = Tag.objects.filter(threadid=thread.thread_id,
                                             list_address=mlist.name)
        except Tag.DoesNotExist:
            thread.tags = []

        # Category XXX to plugin
        thread.category_hk, thread.category_form = \
                get_category_widget(request, thread.category)
        # Unread status
        thread.unread = is_thread_unread(request, mlist.name, thread)

    flash_messages = []
    flash_msg = request.GET.get("msg")
    if flash_msg:
        flash_msg = { "type": FLASH_MESSAGES[flash_msg][0],
                      "msg": FLASH_MESSAGES[flash_msg][1] }
        flash_messages.append(flash_msg)

    context = {
        'mlist' : mlist,
        'threads': threads,
        'participants': len(participants),
        'months_list': get_months(store, mlist.name),
        'flash_messages': flash_messages,
    }
    context.update(extra_context)
    print repr(context)
    return render(request, template_name, context)

class C:
    pass

@check_mlist_private
def overview(request, mlist_fqdn=None):
    if not mlist_fqdn:
        return redirect('/')

    store = get_store(request)
    mlist = store.get_list(mlist_fqdn)
    if mlist is None:
        raise Http404("No archived mailing-list by that name.")
    begin_date, end_date = mlist.get_recent_dates()
    threads_result = store.get_threads(
            list_name=mlist.name, start=begin_date, end=end_date)

    threads = []
    participants = set()
    extra_context = {}
    Thread = namedtuple('Thread', pluginRegistry.thread_indexes)
    for thread_obj in threads_result:
        thrd = C()
        # Core 
        thrd.thread_id = thread_obj.thread_id
        thrd.email_id_hashes = thread_obj.email_id_hashes
        thrd.subject = thread_obj.subject
        thrd.length = len(thread_obj)
        thrd.participants = thread_obj.participants
        print repr(thrd.participants)
        #print thrd.participants_count
        thrd.date_active = thread_obj.date_active.replace(tzinfo=utc)
        thrd.unread = is_thread_unread(request, mlist.name, thread_obj)
        thrd.list_name = mlist.name
        # XXX move to plugins
        thrd.category = get_category_widget(None, thread_obj.category)[0]
        pluginRegistry.thread_view(request, thrd, extra_context)
        thread = Thread(**thrd.__dict__)
        # Statistics on how many participants and threads this month
        participants.update(thread.participants)
        threads.append(thread)

    # top threads are the one with the most answers
    top_threads = sorted(threads, key=lambda t: len(t), reverse=True)

    # active threads are the ones that have the most recent posting
    active_threads = sorted(threads, key=lambda t: t.date_active, reverse=True)

    # top authors are the ones that have the most kudos.  How do we determine
    # that?  Most likes for their post?
    if settings.USE_MOCKUPS:
        authors = generate_top_author()
        authors = sorted(authors, key=lambda author: author.kudos)
        authors.reverse()
    else:
        authors = []

    # Top posters
    top_posters = []
    for poster in store.get_top_participants(list_name=mlist.name,
                start=begin_date, end=end_date, limit=5):
        top_posters.append({"name": poster[0], "email": poster[1],
                            "count": poster[2]})

    # Popular threads 
    #XXX Plugin !!
    pluginRegistry.threads_overview(request,threads,extra_context)
    # Threads by category
    threads_by_category = {}
    for thread in active_threads:
        if not thread.category:
            continue
        # don't use defaultdict, use .setdefault():
        # http://stackoverflow.com/questions/4764110/django-template-cant-loop-defaultdict
        if len(threads_by_category.setdefault(thread.category, [])) >= 5:
            continue
        threads_by_category[thread.category].append(thread)

    context = {
        'view_name': 'overview',
        'mlist' : mlist,
        'most_active_threads': active_threads[:5],
        'top_author': authors,
        'top_posters': top_posters,
        'threads_by_category': threads_by_category,
        'months_list': get_months(store, mlist.name),
    }
    context.update(extra_context)
    return render(request, "overview.html", context)


@check_mlist_private
def recent_activity(request, mlist_fqdn):
    store = get_store(request)
    mlist = store.get_list(mlist_fqdn)
    evolution = get_recent_list_activity(store, mlist)
    return HttpResponse(json.dumps({"evolution": evolution}),
                        content_type='application/javascript')
