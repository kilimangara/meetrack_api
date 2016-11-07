import time

import fakeredis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from authtoken import tokens
from .phone_storage import PhoneStorage
from . import phone_storage

User = get_user_model()


@override_settings(TEST_SMS=True)
class CodeSendingTests(APITestCase):
    url = '/api/auth/code/'
    r = fakeredis.FakeStrictRedis()
    phone_storage.connect(r)

    def setUp(self):
        self.r.flushdb()

    def tearDown(self):
        self.r.flushdb()

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

    def test_limit_exceeded(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_attempts(settings.SMS_AUTH['ATTEMPTS_LIMIT'])
        r = self.client.post(self.url, {'phone': phone_number})
        self.assertEqual(r.status_code, 429)


class PhoneConfirmTests(APITestCase):
    url = '/api/auth/users/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)
    phone_storage.connect(r)

    def setUp(self):
        self.r.flushdb()

    def tearDown(self):
        self.r.flushdb()

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
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 400)

    def test_another_phone_number(self):
        phone = PhoneStorage('+79250741413')
        phone.set_code('00000')
        r = self.client.post(self.url, {'phone': '+79250741412', 'code': '00000'})
        self.assertEqual(r.status_code, 400)

    def test_limit_exceeded(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        phone.set_attempts(settings.SMS_AUTH['ATTEMPTS_LIMIT'])
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 429)

    def test_expire(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000', time=0)
        time.sleep(1)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 400)

    def test_sign_in_token_exists(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        u = User.objects.create(phone=phone_number)
        token = tokens.create(u.id)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 201)
        self.assertNotEqual(r.data['token'], token)
        self.assertEqual(r.data['user_id'], u.id)

    def test_sign_in_new_token(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        u = User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(tokens.authenticate(r.data['token']), u.id)
        self.assertEqual(r.data['user_id'], u.id)

    def test_sign_in_user_not_exists(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': False})
        self.assertEqual(r.status_code, 404)

    def test_sign_up_no_name(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': True, 'name': ''})
        self.assertEqual(r.status_code, 400)
        self.assertIn('name', r.data)

    def test_sign_up_user_exists(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': True, 'name': 'aa'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)

    def test_sign_up_ok(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='00000')
        u1 = User.objects.create(phone='+79250741414')
        u2 = User.objects.create(phone='+79250741412')
        u1.add_to_contacts('+79250741413', 'hello')
        u2.add_to_contacts('+79250741413', 'world')
        with open('registration/test_files/file1.png', 'rb') as f:
            r = self.client.post(
                self.url, {'phone': '+79250741413', 'code': '00000', 'is_new': True, 'name': 'aa', 'avatar': f})
        self.assertEqual(r.status_code, 201)
        user_id = r.data['user_id']
        self.assertEqual(tokens.authenticate(r.data['token']), user_id)
        u = User.objects.get(phone=phone_number)
        self.assertEqual(u.id, user_id)
        self.assertIn(u, u1.contacted_users.all())
        self.assertIn(u, u2.contacted_users.all())
