# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-11 19:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20161011_1901'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='users.User')),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound_blocks', to='users.User')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='blacklist',
            unique_together=set([('user_from', 'user_to')]),
        ),
    ]
