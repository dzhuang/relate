# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0066_alt_course_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatus',
            name='student_ID',
            field=models.CharField(null=True, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid student ID. This value may contain only letters, numbers and @/./+/-/_ characters.', b'invalid')], max_length=40, blank=True, help_text='Filling so that your can enroll some courses automatically.', unique=True, verbose_name='student ID', db_index=True),
        ),
    ]
