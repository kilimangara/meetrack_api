import fakeredis
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from authtoken import tokens
from msg_queue.tests import QueueTestConsumer
from .models import Meeting
from msg_queue import queue
from .views import LEFT_MSG, EXCLUDED_MSG, INVITED_MSG, COMPLETED_MSG

User = get_user_model()


class MeetingCreationTests(APITestCase):
    url = '/api/meetings/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def assert_lists_equal(self, l1, l2):
        self.assertEqual(sorted(l1), sorted(l2))

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741413')

    def test_without_title(self):
        with open('meetings/test_files/file1.png', 'rb') as f:
            r = self.client.post(self.url, data={'logo': f, 'users': [self.u2.id]})
        self.assertEqual(r.status_code, 400)
        self.assertIn('title', r.data)

    def test_without_logo(self):
        r = self.client.post(self.url, data={'logo': '', 'users': [self.u2.id], 'title': '222'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('logo', r.data)

    def test_users_with_creator(self):
        users = [self.u2.id, self.u.id, self.u3.id]
        with open('meetings/test_files/file1.png', 'rb') as f:
            r = self.client.post(self.url, data={'logo': f, 'users': users, 'title': 'sdf'})
        mid = r.data['id']
        m = Meeting.objects.get(id=mid)
        self.assertEqual(m.king_id, self.u.id)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['king'], self.u.id)
        self.assert_lists_equal(r.data['users'], users)

    def test_completed(self):
        users = [self.u2.id, self.u.id, self.u3.id]
        with open('meetings/test_files/file1.png', 'rb') as f:
            r = self.client.post(self.url, data={'logo': f, 'users': users, 'title': 'sdf', 'completed': True})
        self.assertEqual(r.status_code, 201)
        mid = r.data['id']
        m = Meeting.objects.get(id=mid)
        self.assertFalse(m.completed)
        self.assertEqual(r.data['king'], self.u.id)
        self.assertFalse(r.data['completed'])
        self.assert_lists_equal(r.data['users'], users)

    def test_users_without_creator(self):
        users = [self.u2.id, self.u3.id]
        with open('meetings/test_files/file1.png', 'rb') as f:
            r = self.client.post(self.url, data={'logo': f, 'users': users, 'title': 'sdf'})
        mid = r.data['id']
        m = Meeting.objects.get(id=mid)
        self.assertEqual(m.king_id, self.u.id)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['king'], self.u.id)
        self.assert_lists_equal(r.data['users'], users + [self.u.id])

    def test_non_existing_users(self):
        registered = [self.u2.id, self.u3.id, self.u.id]
        non_registered = [228, 322]
        users = registered + non_registered
        with open('meetings/test_files/file1.png', 'rb') as f:
            r = self.client.post(self.url, data={'logo': f, 'users': users, 'title': 'sdf'})
        mid = r.data['id']
        m = Meeting.objects.get(id=mid)
        self.assertEqual(m.king_id, self.u.id)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['king'], self.u.id)
        self.assert_lists_equal(r.data['users'], registered)

    def test_blocked_user(self):
        users = [self.u2.id, self.u3.id]
        self.u2.blocks.create(user_to=self.u)
        with open('meetings/test_files/file1.png', 'rb') as f:
            r = self.client.post(self.url, data={'logo': f, 'users': users, 'title': 'sdf'})
        mid = r.data['id']
        m = Meeting.objects.get(id=mid)
        self.assertEqual(m.king_id, self.u.id)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['king'], self.u.id)
        self.assert_lists_equal(r.data['users'], [self.u3.id, self.u.id])
        self.assertNotIn(self.u2.id, r.data['users'])


class GetMeetingsTests(APITestCase):
    url = '/api/meetings/'
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def assert_ids_equal(self, data, expected):
        self.assertEqual(sorted([x['id'] for x in data]), sorted(expected))

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741413')

    def test_empty(self):
        for _ in range(5):
            m = Meeting.objects.create()
            m.members.create(user=self.u2, king=True)
            m.members.create(user=self.u3)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, [])

    def test_choice(self):
        m1 = Meeting.objects.create()
        m1.members.create(user=self.u, king=True)
        m2 = Meeting.objects.create(completed=True)
        m2.members.create(user=self.u, king=True)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assert_ids_equal(r.data, [m1.id])
        r = self.client.get(self.url, data={'completed': False})
        self.assert_ids_equal(r.data, [m1.id])

    def test_not_king(self):
        m1 = Meeting.objects.create()
        m1.members.create(user=self.u2, king=True)
        m1.members.create(user=self.u)
        m2 = Meeting.objects.create()
        m2.members.create(user=self.u2, king=True)
        m2.members.create(user=self.u)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assert_ids_equal(r.data, [m1.id, m2.id])


class GetSingleMeetingTests(APITestCase):
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741413')
        self.m = Meeting.objects.create()
        self.url = '/api/meetings/{}/'.format(self.m.id)

    def test_not_member(self):
        self.m.members.create(user=self.u2, king=True)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 404)
        self.assertIn('detail', r.data)

    def test_uncompleted(self):
        self.m.members.create(user=self.u2, king=True)
        self.m.members.create(user=self.u)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['id'], self.m.id)

    def test_completed(self):
        self.m.members.create(user=self.u2, king=True)
        self.m.members.create(user=self.u)
        self.m.completed = True
        self.m.save()
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['id'], self.m.id)


class MeetingInviteTests(APITestCase):
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)
    queue.connect(r)
    queue_test_consumer = QueueTestConsumer(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741413')
        self.m = Meeting.objects.create()
        self.url = '/api/meetings/{}/users/'.format(self.m.id)
        self.queue_test_consumer.clean()

    def tearDown(self):
        self.queue_test_consumer.clean()

    def assert_lists_equal(self, l1, l2):
        self.assertEqual(sorted(l1), sorted(l2))

    def test_not_member(self):
        self.m.members.create(user=self.u2, king=True)
        self.m.members.create(user=self.u3)
        r = self.client.put(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 404)
        self.assertIn('detail', r.data)

    def test_completed(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u3)
        self.m.completed = True
        self.m.save()
        r = self.client.put(self.url, data={'user': self.u2.id})
        self.assertEqual(r.status_code, 404)
        self.assertIn('detail', r.data)

    def test_blocked(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        self.u3.blocks.create(user_to=self.u)
        r = self.client.put(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(self.u3, self.m.users.all())
        self.assert_lists_equal(r.data['users'], [self.u.id, self.u2.id])
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_not_king(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.put(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.u3, self.m.users.all())
        self.assert_lists_equal(r.data['users'], [self.u.id, self.u2.id, self.u3.id])
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(),
                         [{'meeting': self.m.id, 'type': INVITED_MSG, 'data': {'user': self.u3.id}}])

    def test_king(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        r = self.client.put(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.u3, self.m.users.all())
        self.assert_lists_equal(r.data['users'], [self.u.id, self.u2.id, self.u3.id])
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(),
                         [{'meeting': self.m.id, 'type': INVITED_MSG, 'data': {'user': self.u3.id}}])

    def test_already_invited(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.put(self.url, data={'user': self.u2.id})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(self.u3, self.m.users.all())
        self.assertIn(self.u2, self.m.users.all())
        self.assert_lists_equal(r.data['users'], [self.u.id, self.u2.id])
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_yourself(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.put(self.url, data={'user': self.u.id})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user', r.data)
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_user_does_not_exist(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.put(self.url, data={'user': 228})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user', r.data)


class MeetingExcludeTests(APITestCase):
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)
    queue.connect(r)
    queue_test_consumer = QueueTestConsumer(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741413')
        self.m = Meeting.objects.create()
        self.url = '/api/meetings/{}/users/'.format(self.m.id)
        self.queue_test_consumer.clean()

    def tearDown(self):
        self.queue_test_consumer.clean()

    def assert_lists_equal(self, l1, l2):
        self.assertEqual(sorted(l1), sorted(l2))

    def test_not_member(self):
        self.m.members.create(user=self.u2, king=True)
        self.m.members.create(user=self.u3)
        r = self.client.delete(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 404)
        self.assertIn('detail', r.data)

    def test_completed(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u3)
        self.m.completed = True
        self.m.save()
        r = self.client.delete(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 404)
        self.assertIn('detail', r.data)

    def test_not_king(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        self.m.members.create(user=self.u3)
        r = self.client.delete(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 403)
        self.assertIn(self.u3, self.m.users.all())
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_success(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        self.m.members.create(user=self.u3)
        r = self.client.delete(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(self.u3, self.m.users.all())
        self.assert_lists_equal(r.data['users'], [self.u.id, self.u2.id])
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(),
                         [{'meeting': self.m.id, 'type': EXCLUDED_MSG, 'data': {'user': self.u3.id}}])

    def test_already_excluded(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        r = self.client.delete(self.url, data={'user': self.u3.id})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(self.u3, self.m.users.all())
        self.assert_lists_equal(r.data['users'], [self.u.id, self.u2.id])
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_yourself(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.delete(self.url, data={'user': self.u.id})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user', r.data)
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_user_does_not_exist(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.delete(self.url, data={'user': 228})
        self.assertEqual(r.status_code, 400)
        self.assertIn('user', r.data)


class MeetingLeaveTests(APITestCase):
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)
    queue.connect(r)
    queue_test_consumer = QueueTestConsumer(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.u2 = User.objects.create(phone='+79250741412')
        self.u3 = User.objects.create(phone='+79250741413')
        self.m = Meeting.objects.create()
        self.url = '/api/meetings/{}/'.format(self.m.id)
        self.queue_test_consumer.clean()

    def tearDown(self):
        self.queue_test_consumer.clean()

    def assert_lists_equal(self, l1, l2):
        self.assertEqual(sorted(l1), sorted(l2))

    def test_not_king(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.m.king_id, self.u2.id)
        self.assertNotIn(self.u, self.m.users.all())
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(),
                         [{'meeting': self.m.id, 'type': LEFT_MSG, 'data': {'user': self.u.id, 'king': self.u2.id}}])

    def test_king(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.m.king_id, self.u2.id)
        self.assertNotIn(self.u, self.m.users.all())
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(),
                         [{'meeting': self.m.id, 'type': LEFT_MSG, 'data': {'user': self.u.id, 'king': self.u2.id}}])

    def test_not_member(self):
        self.m.members.create(user=self.u2, king=True)
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 404)

    def test_completed(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        self.m.completed = True
        self.m.save()
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.m.king_id, self.u2.id)
        self.assertNotIn(self.u, self.m.users.all())
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_last(self):
        self.m.members.create(user=self.u, king=True)
        r = self.client.delete(self.url)
        with self.assertRaises(Meeting.DoesNotExist):
            self.m.refresh_from_db()
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])


class MeetingCompleteTests(APITestCase):
    r = fakeredis.FakeStrictRedis()
    tokens.connect(r)
    queue.connect(r)
    queue_test_consumer = QueueTestConsumer(r)

    def setUp(self):
        self.u = User.objects.create(phone='+79250741414')
        self.u2 = User.objects.create(phone='+79250741412')
        self.token = tokens.create(self.u.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.m = Meeting.objects.create()
        self.url = '/api/meetings/{}/'.format(self.m.id)
        self.queue_test_consumer.clean()

    def tearDown(self):
        self.queue_test_consumer.clean()

    def test_not_king(self):
        self.m.members.create(user=self.u)
        self.m.members.create(user=self.u2, king=True)
        r = self.client.patch(self.url, {'completed': True})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_not_member(self):
        self.m.members.create(user=self.u2, king=True)
        r = self.client.patch(self.url, {'completed': True})
        self.assertEqual(r.status_code, 404)

    def test_not_true(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        r = self.client.patch(self.url, {'completed': False})
        self.assertEqual(r.status_code, 400)
        self.assertIn('completed', r.data)
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(), [])

    def test_success(self):
        self.m.members.create(user=self.u, king=True)
        self.m.members.create(user=self.u2)
        r = self.client.patch(self.url, {'completed': True})
        self.assertEqual(r.status_code, 200)
        self.m.refresh_from_db()
        self.assertEqual(r.data['id'], self.m.id)
        self.assertTrue(r.data['completed'])
        self.assertTrue(self.m.completed)
        self.assertEqual(self.queue_test_consumer.get_meeting_msgs(),
                         [{'meeting': self.m.id, 'type': COMPLETED_MSG, 'data': {}}])
