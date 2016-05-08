# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-08 04:04
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0006_alter_flowsessionimage_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowpageimage',
            name='image_data',
            field=jsonfield.fields.JSONField(blank=True, null=True, verbose_name='Image_Data'),
        ),
        migrations.AddField(
            model_name='flowpageimage',
            name='is_image_textify',
            field=models.BooleanField(default=False, verbose_name=b'Load textified Image?'),
        ),
    ]
