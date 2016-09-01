# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-08 05:43
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0007_add_image_data_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowpageimage',
            name='use_image_data',
            field=models.BooleanField(default=False, verbose_name=b'Use external Image data?'),
        ),
        migrations.AlterField(
            model_name='flowpageimage',
            name='image_data',
            field=jsonfield.fields.JSONField(blank=True, null=True, verbose_name='External image data'),
        ),
        migrations.AlterField(
            model_name='flowpageimage',
            name='image_text',
            field=models.TextField(blank=True, default=b'', help_text='The html for the FlowPageImage', verbose_name='Related Html'),
        ),
    ]