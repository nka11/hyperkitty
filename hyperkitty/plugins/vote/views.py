from voting import set_message_votes
from models import Rating
from hyperkitty.lib import get_store
from django.shortcuts import render
import django.utils.simplejson as json
from django.core.exceptions import SuspiciousOperation
from django.template import RequestContext, loader
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from hyperkitty.lib.mailman import check_mlist_private

@login_required
def votes(request):
    store = get_store(request)
    try:
        votes = Rating.objects.filter(user=request.user)
    except Rating.DoesNotExist:
        votes = []
    for vote in votes:
        vote.message = store.get_message_by_hash_from_list(
                vote.list_address, vote.messageid)
        if vote.message is None:
            vote.delete()
    votes = [ v for v in votes if v.message is not None ]
    return render(request, 'ajax/votes.html', {
                "votes": votes,
            })
            
@check_mlist_private
def message_vote(request, mlist_fqdn, message_id_hash):
    """ Add a rating to a given message identified by messageid. HTTP POST Handler """
    if request.method != 'POST':
        raise SuspiciousOperation

    if not request.user.is_authenticated():
        return HttpResponse('You must be logged in to vote',
                            content_type="text/plain", status=403)

    store = get_store(request)
    message = store.get_message_by_hash_from_list(mlist_fqdn, message_id_hash)
    if message is None:
        raise Http404

    value = int(request.POST['vote'])
    if value not in [-1, 0, 1]:
        raise SuspiciousOperation

    # Checks if the user has already voted for a this message.
    try:
        v = Rating.objects.get(user=request.user, messageid=message_id_hash,
                               list_address=mlist_fqdn)
        if v.vote == value:
            return HttpResponse("You've already cast this vote",
                                content_type="text/plain", status=403)
    except Rating.DoesNotExist:
        if value != 0:
            v = Rating(list_address=mlist_fqdn, messageid=message_id_hash,
                       vote=value)
            v.user = request.user
        else:
            return HttpResponse("There is no vote to cancel",
                                content_type="text/plain", status=500)

    if value == 0:
        v.delete()
    else:
        v.vote = value
        v.save()

    # Extract all the votes for this message to refresh it
    set_message_votes(message, request.user)
    t = loader.get_template('vote/messages/like_form.html')
    html = t.render(RequestContext(request, {
            "object": message,
            "message_id_hash": message_id_hash,
            }))

    result = { "like": message.likes, "dislike": message.dislikes,
               "html": html, }
    return HttpResponse(json.dumps(result),
                        mimetype='application/javascript')
