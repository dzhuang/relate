# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0080_auto_20151220_1357'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={},
        ),
        migrations.AddField(
            model_name='image',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
