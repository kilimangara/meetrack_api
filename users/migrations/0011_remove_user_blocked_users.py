# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 18:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20161012_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='blocked_users',
        ),
    ]