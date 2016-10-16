from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from . import tokens

User = get_user_model()
REDIS_SETTINGS = settings.REDIS
REDIS_SETTINGS['DB'] += 1


@override_settings(REDIS=REDIS_SETTINGS)
class AuthTests(APITestCase):
    url = '/api/account/'
    tokens.connect()

    def setUp(self):
        self.user = User.objects.create()
        tokens.delete_all()

    def tearDown(self):
        tokens.delete_all()

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

    def test_correct_creds(self):
        token = tokens.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_retry_token(self):
        old_token = tokens.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + old_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        new_token = tokens.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + new_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + old_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)
