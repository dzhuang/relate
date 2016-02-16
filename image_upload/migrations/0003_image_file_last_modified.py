# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-16 11:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0002_sessionpage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='file_last_modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
