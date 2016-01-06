# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0083_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(storage=django.core.files.storage.FileSystemStorage(location=b'F:\\tempgit\\relate\\protected'), upload_to=b'download'),
        ),
    ]
