# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-20 05:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'ordering': ['user']},
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user_name',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.FileField(upload_to='avatars/'),
        ),
    ]
