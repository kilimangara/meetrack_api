import fakeredis
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from base_app.error_types import INVALID_AUTH_TOKEN

from . import tokens

User = get_user_model()


class AuthTests(APITestCase):
    url = '/api/account/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.user = User.objects.create()
        self.r.flushdb()

    def tearDown(self):
        self.r.flushdb()

    @classmethod
    def different_token(cls, token):
        if token[0] == 'a':
            token = 'b' + token[1:]
        else:
            token = 'a' + token[1:]
        return token

    def test_incorrect_creds(self):
        token = tokens.create(self.user.id)
        incorrect_token = self.different_token(token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + incorrect_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data['error']['type'], INVALID_AUTH_TOKEN)

    def test_correct_creds(self):
        token = tokens.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('data', r.data)

    def test_retry_token(self):
        old_token = tokens.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + old_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('data', r.data)
        new_token = tokens.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + new_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('data', r.data)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + old_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data['error']['type'], INVALID_AUTH_TOKEN)
