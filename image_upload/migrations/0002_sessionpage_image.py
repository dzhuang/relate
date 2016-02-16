# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionpageimage',
            name='image_page_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
