import base64
import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase


def http_basic_auth_string(username, password):
    credentials = base64.encodestring('%s:%s' % (username, password)).strip()
    auth_string = 'Basic %s' % credentials
    return auth_string


@mock.patch.object(settings, 'ZENDESK_CALLBACK_USERNAME', 'foo')
@mock.patch.object(settings, 'ZENDESK_CALLBACK_PASSWORD', 'bar')
@mock.patch('djzendesk.views.target_callback_received')
class DjangoZendeskTestCase(TestCase):
    def test_view_requires_post(self, mock_target_callback_received):
        url = reverse('zendesk:callback', kwargs={'ticket_id': '123'})

        # Test GET
        response = self.client.get(url, {'message': 'Hello, world!'})
        self.assertEqual(response.status_code, 405)

        # Test PUT
        response = self.client.put(url, {'message': 'Hello, world!'})
        self.assertEqual(response.status_code, 405)

        # Test DELETE
        response = self.client.delete(url, {'message': 'Hello, world!'})
        self.assertEqual(response.status_code, 405)

        # Test HEAD
        response = self.client.head(url, {'message': 'Hello, world!'})
        self.assertEqual(response.status_code, 405)

        # Test POST
        response = self.client.post(url, {'message': 'Hello, world!'})
        self.assertNotEqual(response.status_code, 405)

    def test_view_requires_authentication(self, mock_target_callback_received):
        url = reverse('zendesk:callback', kwargs={'ticket_id': '123'})

        # Test no credentials
        response = self.client.post(url, {'message': 'Hello, world!'})
        self.assertEqual(response.status_code, 403)

        # Test wrong credentials
        auth_string = http_basic_auth_string(username='foo', password='bad')
        response = self.client.post(url, {'message': 'Hello, world!'}, HTTP_AUTHORIZATION=auth_string)
        self.assertEqual(response.status_code, 403)

        # Test correct credentials
        auth_string = http_basic_auth_string(username='foo', password='bar')
        response = self.client.post(url, {'message': 'Hello, world!'}, HTTP_AUTHORIZATION=auth_string)
        self.assertNotEqual(response.status_code, 403)

    def test_view_requires_message(self, mock_target_callback_received):
        url = reverse('zendesk:callback', kwargs={'ticket_id': '123'})
        auth_string = http_basic_auth_string(username='foo', password='bar')

        # Test without message
        response = self.client.post(url, {'blah': 'blah'}, HTTP_AUTHORIZATION=auth_string)
        self.assertEqual(response.status_code, 400)

        # Test with message
        response = self.client.post(url, {'message': 'Hello, world!'}, HTTP_AUTHORIZATION=auth_string)
        self.assertNotEqual(response.status_code, 400)

    def test_view_ok(self, mock_target_callback_received):
        url = reverse('zendesk:callback', kwargs={'ticket_id': '123'})
        auth_string = http_basic_auth_string(username='foo', password='bar')
        response = self.client.post(url, {'message': 'Hello, world!'}, HTTP_AUTHORIZATION=auth_string)
        self.assertContains(response, 'OK')

    def test_view_sends_signal(self, mock_target_callback_received):
        url = reverse('zendesk:callback', kwargs={'ticket_id': '123'})
        auth_string = http_basic_auth_string(username='foo', password='bar')
        response = self.client.post(url, {'message': 'Hello, world!'}, HTTP_AUTHORIZATION=auth_string)
        mock_target_callback_received.send.assert_called_once_with(
            sender=None,
            ticket_id='123',
            message='Hello, world!',
        )
