# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 18:05
from __future__ import unicode_literals

from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20161012_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklist',
            name='user_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(null=True, storage=django.core.files.storage.FileSystemStorage(base_url='http://localhost:8000/media/'), upload_to='images/%Y/%m/%d'),
        ),
    ]