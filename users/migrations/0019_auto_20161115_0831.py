# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-15 08:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20161019_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='created',
            new_name='created_at',
        ),
    ]
