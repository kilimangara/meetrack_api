import unittest
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .serializers import PhoneNumberField, ForeignUserIdSerializer
from rest_framework.exceptions import ValidationError

User = get_user_model()


class TestSerializer(serializers.Serializer):
    phone = PhoneNumberField()


class PhoneFieldTests(unittest.TestCase):
    def test_country_code(self):
        s = TestSerializer(data={'phone': '+9250741413'})
        self.assertFalse(s.is_valid())
        self.assertIn('phone', s.errors)

    def test_long(self):
        s = TestSerializer(data={'phone': '+792507414134'})
        self.assertFalse(s.is_valid())
        self.assertIn('phone', s.errors)

    def test_short(self):
        s = TestSerializer(data={'phone': '+7250741413'})
        self.assertFalse(s.is_valid())
        self.assertIn('phone', s.errors)

    def test_without_plus(self):
        s = TestSerializer(data={'phone': '79250741413'})
        self.assertFalse(s.is_valid())
        self.assertIn('phone', s.errors)

    def test_non_uniform_format(self):
        s = TestSerializer(data={'phone': '89250741413'})
        self.assertFalse(s.is_valid())
        self.assertIn('phone', s.errors)

    def test_correct(self):
        s = TestSerializer(data={'phone': '+79250741413'})
        self.assertTrue(s.is_valid())
        self.assertEqual(s.validated_data['phone'], '+79250741413')


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
