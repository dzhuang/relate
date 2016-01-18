# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0081_course_fields_i18n'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='enroll_deadline',
            field=models.DateField(help_text="After which the course will not be displayed on home page, and enrollment will not be allowed. Leave this field blank if there's no deadline of enrollment.", null=True, verbose_name='Enrollment deadline', blank=True),
        ),
    ]
