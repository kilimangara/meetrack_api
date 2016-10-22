from unittest import TestCase
from rest_framework import serializers
from .serializers import PhoneNumberField


class TestSerializer(serializers.Serializer):
    phone = PhoneNumberField()


class SerializerFieldTests(TestCase):
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
