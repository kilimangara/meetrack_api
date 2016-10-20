# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-17 20:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0003_auto_20161017_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='king',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='kingdoms', to=settings.AUTH_USER_MODEL),
        ),
    ]