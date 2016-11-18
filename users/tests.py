import fakeredis
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from authtoken import tokens
from base_app.error_types import USER_NOT_FOUND

User = get_user_model()


class BlacklistGetTests(APITestCase):
    url = '/api/blacklist/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_empty(self):
        r = self.client.get(self.url)
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data, [])

    def test_exists(self):
        u1 = User.objects.create(phone='+79250741412')
        self.u.blocks.create(user_to=u1)
        r = self.client.get(self.url)
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], u1.id)


class BlacklistAddTests(APITestCase):
    url = '/api/blacklist/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')

    def test_yourself(self):
        r = self.client.put(self.url, data={'user': self.u.id})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user', r.data)

    def test_new_block(self):
        r = self.client.put(self.url, data={'user': self.u2.id})
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.u2.id)
        self.assertIn(self.u2, self.u.blocked_users.all())
        self.assertEqual(len(self.u.blocked_users.all()), 1)

    def test_block_already_blocked(self):
        self.u.blocks.create(user_to_id=self.u2.id)
        r = self.client.put(self.url, data={'user': self.u2.id})
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.u2.id)
        self.assertIn(self.u2, self.u.blocked_users.all())
        self.assertEqual(len(self.u.blocked_users.all()), 1)

    def test_non_existent_user(self):
        self.u.blocks.create(user_to_id=self.u2.id)
        r = self.client.put(self.url, data={'user': self.u2.id + 228})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error']['type'], USER_NOT_FOUND)
        self.assertEqual(len(self.u.blocked_users.all()), 1)


class BlackListDeleteTests(APITestCase):
    url = '/api/blacklist/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741415')

    def test_yourself(self):
        r = self.client.delete(self.url, data={'user': self.u.id})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user', r.data)

    def test_success(self):
        self.u.blocks.create(user_to=self.u2)
        self.u.blocks.create(user_to=self.u3)
        r = self.client.delete(self.url, data={'user': self.u2.id})
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.u3.id)
        self.assertIn(self.u3, self.u.blocked_users.all())
        self.assertNotIn(self.u2, self.u.blocked_users.all())
        self.assertEqual(len(self.u.blocked_users.all()), 1)

    def test_non_existent_user(self):
        self.u.blocks.create(user_to_id=self.u2.id)
        r = self.client.delete(self.url, data={'user': self.u2.id + 228})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error']['type'], USER_NOT_FOUND)
        self.assertEqual(len(self.u.blocked_users.all()), 1)


class ContactsGetTests(APITestCase):
    url = '/api/contacts/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_empty(self):
        r = self.client.get(self.url)
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data, [])

    def test_exists(self):
        u1 = User.objects.create(phone='+79250741412')
        self.u.contacts.create(user_to=u1)
        r = self.client.get(self.url)
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], u1.id)


class ContactsImportTests(APITestCase):
    url = '/api/contacts/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741413')
        self.token = tokens.create(self.u.id)
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
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertIn(self.u2, self.u.contacted_users.all())
        self.assertIn(self.u3, self.u.contacted_users.all())
        for c in data:
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
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertIn(self.u2, self.u.contacted_users.all())
        self.assertIn(self.u3, self.u.contacted_users.all())
        for c in data:
            if c['phone'] == self.u2.phone:
                c['name'] = 'hello'
            elif c['phone'] == self.u3.phone:
                c['name'] = 'world'
            else:
                raise Exception()


class ContactsDeleteTests(APITestCase):
    url = '/api/contacts/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def test_success(self):
        u = User.objects.create(phone='+79250741413')
        token = tokens.create(u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        u2 = User.objects.create(phone='+79250741414')
        u3 = User.objects.create(phone='+79250741412')
        u.contacts.create(user_to=u2, phone=u2.phone)
        u.contacts.create(user_to=u3, phone=u3.phone)
        phones = ['+79250741413', u3.phone, '+79250741416']
        r = self.client.delete(self.url, {'phones': phones})
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], u2.id)
        self.assertIn(u2, u.contacted_users.all())
        self.assertNotIn(u3, u.contacted_users.all())


class UserRepresentationTests(APITestCase):
    url = '/api/users/{}/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.viewer = User.objects.create(phone='+79250741413')
        self.token = tokens.create(self.viewer.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u = User.objects.create(phone='+79250741414', name='hello')

    def test_hidden_and_contact(self):
        self.u.hidden_phone = True
        self.u.save()
        self.viewer.add_to_contacts(self.u.phone, 'world')
        r = self.client.get(self.url.format(self.u.id))
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['name'], 'world')
        self.assertEqual(data['phone'], '+79250741414')

    def test_blocked_and_contact(self):
        self.u.add_to_blacklist(self.viewer.id)
        self.viewer.add_to_contacts(self.u.phone, 'world')
        r = self.client.get(self.url.format(self.u.id))
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['name'], 'world')
        self.assertEqual(data['phone'], '+79250741414')

    def test_blocked(self):
        self.u.add_to_blacklist(self.viewer.id)
        r = self.client.get(self.url.format(self.u.id))
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['name'], 'hello')
        self.assertNotIn('phone', data)

    def test_hidden(self):
        self.u.hidden_phone = True
        self.u.save()
        r = self.client.get(self.url.format(self.u.id))
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['name'], 'hello')
        self.assertNotIn('phone', data)

    def test_simple(self):
        r = self.client.get(self.url.format(self.u.id))
        data = r.data['data']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['name'], 'hello')
        self.assertEqual(data['phone'], '+79250741414')

    def test_non_existent_user(self):
        r = self.client.get(self.url.format(self.u.id + 228))
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['error']['type'], USER_NOT_FOUND)


class AccountTests(APITestCase):
    url = '/api/account/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.name = 'hello'
        self.phone = '+79250471414'
        self.u = User.objects.create(phone=self.phone, name=self.name)
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_delete(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 204)
        with self.assertRaises(tokens.AuthenticationFailed):
            tokens.authenticate(self.token)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_get(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        data = r.data['data']
        self.assertIsNone(data['avatar'])
        self.assertEqual(self.u.name, data['name'])
        self.assertEqual(self.u.id, data['id'])
        self.assertEqual(self.u.phone, data['phone'])
        self.assertEqual(self.u.hidden_phone, data['hidden_phone'])

    def test_update_phone(self):
        new_phone = '+79250741413'
        r = self.client.patch(self.url, data={'phone': new_phone})
        data = r.data['data']
        self.u.refresh_from_db()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['phone'], self.phone)
        self.assertNotEqual(self.u.phone, new_phone)

    def test_update_name(self):
        new_name = 'world'
        r = self.client.patch(self.url, data={'name': new_name})
        data = r.data['data']
        self.u.refresh_from_db()
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(data['name'], self.name)
        self.assertEqual(self.u.name, new_name)

    def test_update_hidden_phone(self):
        self.u.hidden_phone = True
        self.u.save()
        r = self.client.patch(self.url, data={'hidden_phone': False})
        data = r.data['data']
        self.u.refresh_from_db()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['hidden_phone'], False)
        self.assertEqual(self.u.hidden_phone, False)

    def test_update_avatar(self):
        self.assertFalse(self.u.avatar)
        with open('users/test_files/file1.png', 'rb') as f:
            r = self.client.patch(self.url, data={'avatar': f})
        data = r.data['data']
        self.u.refresh_from_db()
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(data['avatar'])
        self.assertTrue(self.u.avatar)
        self.assertEqual(data['avatar'], self.u.avatar.url)

    def test_update_avatar_not_image(self):
        self.assertFalse(self.u.avatar)
        with open('users/test_files/file2.png', 'rb') as f:
            r = self.client.patch(self.url, data={'avatar': f})
        self.assertEqual(r.status_code, 400)
        self.assertIn('avatar', r.data)
        self.u.refresh_from_db()
        self.assertFalse(self.u.avatar)
