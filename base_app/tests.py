from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from users.models import User
from .serializers import ForeignUserIdSerializer


class ForeignUserIdSerializerTests(APITestCase):
    def test_viewer(self):
        u = User.objects.create(phone='+79250741413')
        s = ForeignUserIdSerializer(data={'user': u.id}, context={'viewer': u})
        with self.assertRaises(ValidationError) as e:
            s.is_valid(raise_exception=True)
        self.assertIn('user', e.exception.detail)

    def test_not_viewer(self):
        u = User.objects.create(phone='+79250741413')
        s = ForeignUserIdSerializer(data={'user': u.id + 1}, context={'viewer': u})
        s.is_valid(raise_exception=True)
        self.assertEqual(s.validated_data['user'], u.id + 1)
