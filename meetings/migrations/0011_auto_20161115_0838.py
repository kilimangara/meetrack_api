# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-15 08:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0010_auto_20161115_0831'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='time',
            new_name='end_at',
        ),
    ]