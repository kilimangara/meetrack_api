# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-11 18:56
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_hidden_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(null=True, storage=django.core.files.storage.FileSystemStorage(base_url='http://localhost:8000/media/'), upload_to=''),
        ),
    ]
