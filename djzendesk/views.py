import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from djzendesk.signals import target_callback_received


@csrf_exempt
def callback(request, ticket_id):
    """Handle HTTP callback requests from Zendesk"""

    # Require POST. Anything less is uncivilized.
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['GET'])

    # Extract the message
    if not 'message' in request.POST:
        return HttpResponseBadRequest()

    # TODO: check HTTP basic auth

    message = request.POST['message']

    logging.info("HTTP callback received from Zendesk for ticket %s: %s", ticket_id, message)

    # Fire the signal to notify listeners of received target callback
    target_callback_received.send(sender=__name__, ticket_id=ticket_id, message=message)

    return HttpResponse('OK')
