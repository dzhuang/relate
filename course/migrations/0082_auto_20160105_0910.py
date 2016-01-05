# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0081_auto_20151231_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='creator',
            field=models.ForeignKey(verbose_name='Creator', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(upload_to=b'pictures'),
        ),
    ]
