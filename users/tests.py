from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from authentication import token_storage

User = get_user_model()

REDIS_SETTINGS = settings.REDIS
REDIS_SETTINGS['DB'] += 1


@override_settings(REDIS=REDIS_SETTINGS)
class BlacklistGetTests(APITestCase):
    url = '/api/blacklist/'
    token_storage.connect()

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = token_storage.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_empty(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, [])

    def test_exists(self):
        u1 = User.objects.create(phone='+79250741412')
        u2 = User.objects.create(phone='+79250741414')
        self.u.blocks.create(user_to=u1)
        self.u.blocks.create(user_to=u2, active=False)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['id'], u1.id)


@override_settings(REDIS=REDIS_SETTINGS)
class BlacklistAddTests(APITestCase):
    url = '/api/blacklist/'
    token_storage.connect()

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = token_storage.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')

    def test_user_does_not_exist(self):
        r = self.client.put(self.url, data={'user_id': 228})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user_id', r.data)

    def test_yourself(self):
        r = self.client.put(self.url, data={'user_id': self.u.id})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user_id', r.data)

    def test_new_block(self):
        r = self.client.put(self.url, data={'user_id': self.u2.id})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['id'], self.u2.id)
        self.assertIn(self.u2, self.u.blocked_users())

    def test_exists_block(self):
        self.u.blocks.create(user_to=self.u2, active=False)
        r = self.client.put(self.url, data={'user_id': self.u2.id})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['id'], self.u2.id)
        self.assertIn(self.u2, self.u.blocked_users())


@override_settings(REDIS=REDIS_SETTINGS)
class BlackListDeleteTests(APITestCase):
    url = '/api/blacklist/'
    token_storage.connect()

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = token_storage.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741415')

    def test_user_does_not_exist(self):
        r = self.client.delete(self.url, data={'user_id': 228})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user_id', r.data)

    def test_yourself(self):
        r = self.client.delete(self.url, data={'user_id': self.u.id})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user_id', r.data)

    def test_success(self):
        self.u.blocks.create(user_to=self.u2)
        self.u.blocks.create(user_to=self.u3)
        r = self.client.delete(self.url, data={'user_id': self.u2.id})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['id'], self.u3.id)
        self.assertIn(self.u3, self.u.blocked_users())
        self.assertNotIn(self.u2, self.u.blocked_users())


@override_settings(REDIS=REDIS_SETTINGS)
class ContactsGetTests(APITestCase):
    url = '/api/contacts/'
    token_storage.connect()

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = token_storage.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_empty(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, [])

    def test_exists(self):
        u1 = User.objects.create(phone='+79250741412')
        u2 = User.objects.create(phone='+79250741414')
        self.u.contacts.create(user_to=u1)
        self.u.contacts.create(user_to=u2, active=False)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['id'], u1.id)


@override_settings(REDIS=REDIS_SETTINGS)
class ContactsImportTests(APITestCase):
    url = '/api/contacts/'
    token_storage.connect()

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = token_storage.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741414')
        self.u3 = User.objects.create(phone='+79250741412')

    def test_duplicates(self):
        names = ['aaa', 'hhh', 'ffh']
        phones = ['+79250741415', '+79250741416', '+79250741416']
        r = self.client.put(self.url, data={'names': names, 'phones': phones})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phones', r.data)

    def test_different_len(self):
        names = ['aaa', 'hhh', 'ffh']
        phones = ['+79250741415', '+79250741416']
        r = self.client.put(self.url, data={'names': names, 'phones': phones})
        self.assertEqual(r.status_code, 400)
        self.assertIn('non_field_errors', r.data)

    def test_with_own_phone(self):
        names = ['aaa', 'hhh', 'ffh']
        phones = ['+79250741415', '+79250741416', '+79250741413']
        r = self.client.put(self.url, data={'names': names, 'phones': phones})
        self.assertEqual(r.status_code, 400)
        self.assertIn('phones', r.data)

    def test_new_contacts(self):
        names = ['hello', 'world', 'booo']
        phones = [self.u2.phone, self.u3.phone, '+79250741415']
        r = self.client.put(self.url, data={'names': names, 'phones': phones})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)
        self.assertIn(self.u2, self.u.contacted_users())
        self.assertIn(self.u3, self.u.contacted_users())
        for c in r.data:
            if c['phone'] == self.u2.phone:
                c['name'] = 'hello'
            elif c['phone'] == self.u3.phone:
                c['name'] = 'world'
            else:
                raise Exception()

    def test_exists_contacts(self):
        names = ['hello', 'world', 'booo']
        phones = [self.u2.phone, self.u3.phone, '+79250741415']
        self.u.contacts.create(user_to=self.u2, phone=self.u2.phone, name='olleh')
        self.u.contacts.create(user_to=self.u3, phone=self.u3.phone, name='dlrow')
        r = self.client.put(self.url, data={'names': names, 'phones': phones})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)
        self.assertIn(self.u2, self.u.contacted_users())
        self.assertIn(self.u3, self.u.contacted_users())
        for c in r.data:
            if c['phone'] == self.u2.phone:
                c['name'] = 'hello'
            elif c['phone'] == self.u3.phone:
                c['name'] = 'world'
            else:
                raise Exception()


@override_settings(REDIS=REDIS_SETTINGS)
class ContactsImportTests(APITestCase):
    url = '/api/contacts/'
    token_storage.connect()

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = token_storage.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741414')
        self.u3 = User.objects.create(phone='+79250741412')
