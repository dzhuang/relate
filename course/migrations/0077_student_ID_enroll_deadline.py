# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0076_alter_model_examticket_add_i18n'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='course_status',
        ),
        migrations.AddField(
            model_name='course',
            name='enroll_deadline',
            field=models.DateField(help_text="After which the course will not be displayed on home page, and enrollment will not be allowed. Leave this field blank if there's no deadline of enrollment.", null=True, verbose_name='Enrollment deadline', blank=True),
        ),
        migrations.AlterField(
            model_name='userstatus',
            name='student_ID',
            field=models.CharField(null=True, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid student ID. This value may contain only letters, numbers and @/./+/-/_ characters.', b'invalid')], max_length=40, blank=True, help_text='Not required. Filling so that your can enroll some courses automatically. Once confirmed it is not changable.', unique=True, verbose_name='student ID', db_index=True),
        ),
    ]
