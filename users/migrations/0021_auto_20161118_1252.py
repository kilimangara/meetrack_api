# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-18 12:52
from __future__ import unicode_literals

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_user_tmp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='tmp',
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=255, unique=True),
        ),
    ]
