from hyperkitty.models import LastView
from django.utils.timezone import utc

def is_thread_unread(request, thread):
    """Returns True or False if the thread is unread or not."""
    unread = False
    if request.user.is_authenticated():
        try:
            last_view_obj = LastView.objects.get(
                    list_address=thread.list_name,
                    threadid=thread.thread_id,
                    user=request.user)
        except LastView.DoesNotExist:
            unread = True
        else:
            if thread.date_active.replace(tzinfo=utc) \
                    > last_view_obj.view_date:
                unread = True
    return unread
