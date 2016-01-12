# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0075_course_metadata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='examticket',
            options={'ordering': ('exam__course', '-creation_time'), 'verbose_name': 'Exam ticket', 'verbose_name_plural': 'Exam tickets', 'permissions': (('can_issue_exam_tickets', 'Can issue exam tickets to student'),)},
        ),
        migrations.AlterField(
            model_name='course',
            name='course_root_path',
            field=models.CharField(help_text='Subdirectory <b>within</b> the git repository to use as course root directory. Not required, and usually blank. Use only if your course content lives in a subdirectory of your git repository. Should not include trailing slash.', max_length=200, verbose_name='Course root in repository', blank=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(help_text="A human-readable name for the course. (e.g. 'Numerical Methods')", max_length=200, null=True, verbose_name='Course name'),
        ),
        migrations.AlterField(
            model_name='course',
            name='number',
            field=models.CharField(help_text="A human-readable course number/ID for the course (e.g. 'CS123')", max_length=200, null=True, verbose_name='Course number'),
        ),
        migrations.AlterField(
            model_name='course',
            name='time_period',
            field=models.CharField(help_text="A human-readable description of the time period for the course (e.g. 'Fall 2014')", max_length=200, null=True, verbose_name='Time Period'),
        ),
    ]
