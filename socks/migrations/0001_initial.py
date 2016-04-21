# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatUser',
            fields=[
                ('userID', models.IntegerField(serialize=False, primary_key=True)),
                ('username', models.CharField(max_length=20)),
                ('access_token', models.CharField(max_length=255)),
                ('access_token_secret', models.CharField(max_length=255)),
                ('is_chat_user', models.BooleanField(default=False)),
                ('last_accessed', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=20)),
                ('message', models.TextField(max_length=120)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
