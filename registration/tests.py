import time

import fakeredis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from authtoken import tokens
from . import phone_storage
from base_app.error_types import INVALID_PHONE_CODE, INVALID_PHONE_NUMBER, CONFIRM_ATTEMPTS_EXCEEDED
from base_app.error_types import USER_NOT_FOUND, USER_ALREADY_EXISTS
from .phone_storage import PhoneStorage

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
        data = r.data['data']
        self.assertEqual(data['is_new'], False)

    def test_new_user(self):
        phone = '+79250741413'
        r = self.client.post(self.url, {'phone': phone})
        self.assertEqual(r.status_code, 201)
        data = r.data['data']
        self.assertEqual(data['is_new'], True)

    def test_empty(self):
        r = self.client.post(self.url, {'phone': ''})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_NUMBER)

    def test_incorrect(self):
        r = self.client.post(self.url, {'phone': '+792507414132'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_NUMBER)


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
        r = self.client.post(self.url, {'phone': '', 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phone', r.data)

    def test_no_code(self):
        r = self.client.post(self.url, {'phone': '+79250741413', 'code': '', 'is_new': False})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_CODE)

    def test_incorrect_code(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        r = self.client.post(self.url, {'phone': phone_number, 'code': '21111', 'is_new': False})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_CODE)

    def test_another_phone_number(self):
        phone = PhoneStorage('+79250741413')
        phone.set_code('11111')
        r = self.client.post(self.url, {'phone': '+79250741412', 'code': '11111'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_CODE)

    def test_limit_exceeded(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        phone.set_attempts(settings.SMS_AUTH['ATTEMPTS_LIMIT'])
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r.data['error']['type'], CONFIRM_ATTEMPTS_EXCEEDED)

    def test_expire(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111', lifetime=0)
        time.sleep(1)
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_CODE)

    def test_sign_in_token_exists(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        u = User.objects.create(phone=phone_number)
        old_token = tokens.create(u.id)
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        data = r.data['data']
        self.assertEqual(r.status_code, 201)
        self.assertNotEqual(data['token'], old_token)
        self.assertEqual(tokens.authenticate(data['token']), u.id)
        with self.assertRaises(tokens.AuthenticationFailed):
            tokens.authenticate(old_token)
        self.assertEqual(data['user'], u.id)
        with self.assertRaises(PhoneStorage.DoesNotExist):
            phone.get_code()

    def test_sign_in_new_token(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        u = User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        data = r.data['data']
        self.assertEqual(r.status_code, 201)
        self.assertEqual(tokens.authenticate(data['token']), u.id)
        self.assertEqual(data['user'], u.id)
        with self.assertRaises(PhoneStorage.DoesNotExist):
            phone.get_code()

    def test_sign_in_user_not_exists(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error']['type'], USER_NOT_FOUND)
        self.assertEqual('11111', phone.get_code())

    def test_sign_up_no_name(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': True, 'name': ''})
        self.assertEqual(r.status_code, 400)
        self.assertIn('name', r.data)

    def test_sign_up_incorrect_avatar(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        with open('registration/test_files/file2.mp4', 'rb') as f:
            r = self.client.post(self.url,
                                 {'phone': phone_number, 'code': '11111', 'is_new': True, 'name': 'g', 'avatar': f})
        self.assertEqual(r.status_code, 400)
        self.assertIn('avatar', r.data)

    def test_sign_up_user_exists(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': True, 'name': 'aa'})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.data['error']['type'], USER_ALREADY_EXISTS)

    def test_sign_up_ok(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        u1 = User.objects.create(phone='+79250741414')
        u2 = User.objects.create(phone='+79250741412')
        u1.contacts.create(phone=phone_number, name='hello')
        u2.contacts.create(phone=phone_number, name='world')
        with open('registration/test_files/file1.png', 'rb') as f:
            r = self.client.post(
                self.url, {'phone': phone_number, 'code': '11111', 'is_new': True, 'name': 'aa', 'avatar': f})
        self.assertEqual(r.status_code, 201)
        data = r.data['data']
        user_id = data['user']
        self.assertEqual(tokens.authenticate(data['token']), user_id)
        u = User.objects.get(phone=phone_number)
        self.assertEqual(u.id, user_id)
        self.assertIn(u, u1.contacted_users.all())
        self.assertIn(u, u2.contacted_users.all())

    def test_sign_up_after_success_sign_in(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        u = User.objects.create(phone=phone_number)
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        data = r.data['data']
        self.assertEqual(r.status_code, 201)
        self.assertEqual(tokens.authenticate(data['token']), u.id)
        self.assertEqual(data['user'], u.id)
        with open('registration/test_files/file1.png', 'rb') as f:
            r = self.client.post(
                self.url, {'phone': phone_number, 'code': '11111', 'is_new': True, 'name': 'aa', 'avatar': f})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['error']['type'], INVALID_PHONE_CODE)

    def test_sign_up_after_unsuccess_sign_in(self):
        phone_number = '+79250741413'
        phone = PhoneStorage(phone_number)
        phone.set_code(code='11111')
        r = self.client.post(self.url, {'phone': phone_number, 'code': '11111', 'is_new': False})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error']['type'], USER_NOT_FOUND)
        r = self.client.post(
            self.url, {'phone': phone_number, 'code': '11111', 'is_new': True, 'name': 'aa'})
        self.assertEqual(r.status_code, 201)
        data = r.data['data']
        user_id = data['user']
        self.assertEqual(tokens.authenticate(data['token']), user_id)
        u = User.objects.get(phone=phone_number)
        self.assertEqual(u.id, user_id)
        with self.assertRaises(PhoneStorage.DoesNotExist):
            phone.get_code()
