# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import course.models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0082_add_Image_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='thumbnail',
            field=models.ImageField(storage=course.models.UserImageStorage(), upload_to=course.models.user_directory_path, blank=True),
        ),
    ]
