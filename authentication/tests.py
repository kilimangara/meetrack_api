import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from . import phone_storage
from . import token_storage
from .phone_storage import Phone

User = get_user_model()

REDIS_SETTINGS = settings.REDIS
REDIS_SETTINGS['DB'] += 1


@override_settings(REDIS=REDIS_SETTINGS)
class CodeSendingTests(APITestCase):
    url = '/api/auth/code/'
    phone_storage.connect()

    def setUp(self):
        phone_storage.delete_all()

    def tearDown(self):
        phone_storage.delete_all()

    def test_user_exists(self):
        phone = '+79250741413'
        User.objects.create(phone=phone)
        r = self.client.post(self.url, {'phone': phone})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['is_new'], False)

    def test_new_user(self):
        phone = '+79250741413'
        r = self.client.post(self.url, {'phone': phone})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['is_new'], True)

    def test_empty(self):
        r = self.client.post(self.url, {'phone': ''})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)

    def test_incorrect(self):
        r = self.client.post(self.url, {'phone': '+9250741413'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)
        r = self.client.post(self.url, {'phone': '+792507414134'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)
        r = self.client.post(self.url, {'phone': '+7250741413'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)
        r = self.client.post(self.url, {'phone': '79250741413'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)
        r = self.client.post(self.url, {'phone': '89250741413'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)

    def test_limit_exceeded(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.set_attempts(settings.SMS_AUTH['ATTEMPTS_LIMIT'])
        r = self.client.post(self.url, {'phone': phone_number})
        self.assertEqual(r.status_code, 429)


@override_settings(REDIS=REDIS_SETTINGS)
class PhoneConfirmTests(APITestCase):
    url = '/api/auth/users/'
    phone_storage.connect()
    token_storage.connect()

    def setUp(self):
        phone_storage.delete_all()
        token_storage.delete_all()

    def tearDown(self):
        phone_storage.delete_all()
        token_storage.delete_all()

    def test_no_phone(self):
        r = self.client.post(self.url, {'phone': '', 'code': 228, 'is_new': False})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)

    def test_no_code(self):
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '', 'is_new': False})
        self.assertEqual(r.status_code, 400)
        self.assertIn('code', r.data)

    def test_incorrect_code(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 400)

    def test_limit_exceeded(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000', attempts=settings.SMS_AUTH['ATTEMPTS_LIMIT'])
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 429)

    def test_expire(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000', time=0)
        time.sleep(1)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 400)

    def test_sign_in_token_exists(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        u = User.objects.create(phone=phone_number)
        token = token_storage.create(u.id)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 201)
        self.assertNotEqual(r.data['token'], token)
        self.assertEqual(r.data['user_id'], u.id)

    def test_sign_in_new_token(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        u = User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(token_storage.authenticate(r.data['token']), u.id)
        self.assertEqual(r.data['user_id'], u.id)

    def test_sign_in_user_not_exists(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 404)

    def test_sign_up_no_name(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': True, 'name': ''})
        self.assertEqual(r.status_code, 400)
        self.assertIn('name', r.data)

    def test_sign_up_user_exists(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': True, 'name': 'aa'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)

    def test_sign_up_ok(self):
        phone_number = '+79250741413'
        phone = Phone(phone_number)
        phone.create(code='00000')
        u1 = User.objects.create(phone='+79250741414')
        u2 = User.objects.create(phone='+79250741412')
        u1.add_to_contacts('+79250741413', 'hello')
        u2.add_to_contacts('+79250741413', 'world')
        with open('authentication/test_files/file1.png', 'rb') as f:
            r = self.client.post(
                self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': True, 'name': 'aa', 'avatar': f})
        self.assertEqual(r.status_code, 201)
        user_id = r.data['user_id']
        self.assertEqual(token_storage.authenticate(r.data['token']), user_id)
        u = User.objects.get(phone=phone_number)
        self.assertEqual(u.id, user_id)
        self.assertIn(u, u1.contacted_users())
        self.assertIn(u, u2.contacted_users())


@override_settings(REDIS=REDIS_SETTINGS)
class AuthTests(APITestCase):
    url = '/api/account/'
    token_storage.connect()

    def setUp(self):
        self.user = User.objects.create()
        token_storage.delete_all()

    def tearDown(self):
        token_storage.delete_all()

    @classmethod
    def different_token(cls, token):
        if token[0] == 'a':
            token = 'b' + token[1:]
        else:
            token = 'a' + token[1:]
        return token

    def test_incorrect_creds(self):
        token = token_storage.create(self.user.id)
        incorrect_token = self.different_token(token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + incorrect_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_correct_creds(self):
        token = token_storage.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_retry_token(self):
        old_token = token_storage.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + old_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        new_token = token_storage.create(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + new_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + old_token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)
