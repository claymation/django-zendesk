import base64
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from djzendesk.signals import target_callback_received


def is_authenticated(request, username, password):
    """Authenticate the request using HTTP Basic authorization"""
    authenticated = False
    if 'HTTP_AUTHORIZATION' in request.META:
        print request.META['HTTP_AUTHORIZATION']
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                provided_username, provided_password = base64.b64decode(auth[1]).split(':')
                if username == provided_username and password == provided_password:
                    authenticated = True
    return authenticated

@csrf_exempt
def callback(request, ticket_id):
    """Handle HTTP callback requests from Zendesk"""

    # Require POST. Anything else would be uncivilized.
    if not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    username = getattr(settings, 'ZENDESK_CALLBACK_USERNAME', None)
    password = getattr(settings, 'ZENDESK_CALLBACK_PASSWORD', None)

    # Authenticate the request if credentials have been configured
    if username is not None and password is not None:
        if not is_authenticated(request, username, password):
            return HttpResponseForbidden()

    # Extract the message
    if not 'message' in request.POST:
        return HttpResponseBadRequest()

    message = request.POST['message']

    logging.info("HTTP callback received from Zendesk for ticket %s: %s", ticket_id, message)

    # Fire the signal to notify listeners of received target callback
    target_callback_received.send(sender=__name__, ticket_id=ticket_id, message=message)

    return HttpResponse('OK')
