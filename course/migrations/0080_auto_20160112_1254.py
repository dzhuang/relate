# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0079_sessionpageimage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('id', 'creation_time')},
        ),
        migrations.AddField(
            model_name='image',
            name='creation_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
