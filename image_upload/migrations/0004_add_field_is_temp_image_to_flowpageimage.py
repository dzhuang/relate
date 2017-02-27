# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-26 15:16
from __future__ import unicode_literals

from django.db import migrations, models
import image_upload.models
import image_upload.storages


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0003_image_field_max_length_500'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowpageimage',
            name='is_temp_image',
            field=models.BooleanField(default=False, verbose_name='Is the image for temporary use?'),
        ),
        migrations.AlterField(
            model_name='flowpageimage',
            name='image',
            field=models.ImageField(max_length=500, storage=image_upload.models.UserImageStorage(), upload_to=image_upload.models.user_flowsession_img_path),
        ),
        migrations.RemoveField(
            model_name='flowpageimage',
            name='order',
        ),
    ]
