# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 18:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20161012_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='users.User')),
                ('to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inbound_contacts', to='users.User')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set([('owner', 'to')]),
        ),
    ]
