from django.conf.urls.defaults import *

urlpatterns = patterns('djzendesk.views',
    url(r'callback/ticket/(?P<ticket_id>\w+)/$', 'callback', name='callback'),
)
