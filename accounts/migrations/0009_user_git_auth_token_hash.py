# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_inst_id_unique_and_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='git_auth_token_hash',
            field=models.CharField(blank=True, help_text='A hash of the authentication token to be used for direct git access.', max_length=200, null=True, verbose_name='Hash of git authentication token'),
        ),
    ]
