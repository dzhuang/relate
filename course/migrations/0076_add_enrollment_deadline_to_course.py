# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0075_course_metadata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='examticket',
            options={'ordering': ('exam__course', '-creation_time'), 'verbose_name': 'Exam ticket', 'verbose_name_plural': 'Exam tickets', 'permissions': (('can_issue_exam_tickets', 'Can issue exam tickets to student'),)},
        ),
        migrations.AddField(
            model_name='course',
            name='enroll_deadline',
            field=models.DateField(help_text="After which the course will not be displayed on home page, and enrollment will not be allowed. Leave this field blank if there's no deadline of enrollment.", null=True, verbose_name='Enrollment deadline', blank=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='number',
            field=models.CharField(help_text="A human-readable course number/ID for the course (e.g. 'CS123')", max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='userstatus',
            name='student_ID',
            field=models.CharField(null=True, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid student ID. This value may contain only letters, numbers and @/./+/-/_ characters.', b'invalid')], max_length=40, blank=True, help_text='Not required. Filling so that your can enroll some courses automatically. Once confirmed it is not changable.', unique=True, verbose_name='student ID', db_index=True),
        ),
    ]
