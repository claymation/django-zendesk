from django.dispatch import Signal

# This signal is sent when an HTTP target callback is received from Zendesk
target_callback_received = Signal(providing_args=["ticket_id", "message"])
