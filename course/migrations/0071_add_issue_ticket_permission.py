# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0071_merge_with_local'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='examticket',
            options={'ordering': ('exam__course', 'exam', 'usage_time'), 'verbose_name': 'Exam ticket', 'verbose_name_plural': 'Exam tickets', 'permissions': (('can_issue_exam_tickets', 'Can issue exam tickets to student'),)},
        ),
    ]
