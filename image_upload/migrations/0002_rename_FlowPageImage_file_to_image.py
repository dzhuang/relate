# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-21 05:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0001_squashed_0013_remove_UserImage_model_modify_storage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flowpageimage',
            old_name='file',
            new_name='image',
        ),
    ]