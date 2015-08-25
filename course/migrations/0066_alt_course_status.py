# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0065_course_course_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_status',
            field=models.CharField(default=b'open', help_text='The current status of the course. If ended, only Participants can see the course from his/her home page ', max_length=50, verbose_name='Course status', choices=[(b'open', 'Open'), (b'inprogress', 'In_Progress'), (b'ended', 'Ended')]),
        ),
    ]
