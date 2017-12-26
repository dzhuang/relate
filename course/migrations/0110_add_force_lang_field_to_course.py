# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-20 10:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0109_add_manage_authentication_tokens_permssion'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='force_lang',
            field=models.CharField(blank=True, default=None, help_text="Which language is forced to be used for this course. If not set, displayed language will be determined by user browser preference", max_length=200, null=True, verbose_name='Course language forcibly used'),
        ),
    ]
