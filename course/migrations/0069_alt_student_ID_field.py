# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0068_merge_student_ID_and_flowssesion_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatus',
            name='No_ID',
            field=models.BooleanField(default=False, help_text='I am not a student or I have no student ID.', verbose_name='No student ID'),
        ),
        migrations.AddField(
            model_name='userstatus',
            name='student_ID_confirm',
            field=models.CharField(null=True, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid student ID. This value may contain only letters, numbers and @/./+/-/_ characters.', b'invalid')], max_length=40, blank=True, unique=True, verbose_name='student ID confirmation', db_index=True),
        ),
        migrations.AlterField(
            model_name='userstatus',
            name='editor_mode',
            field=models.CharField(default=b'default', help_text='Your favorite text editor mode for text block or code block.', max_length=20, verbose_name='Editor mode', choices=[(b'default', 'Default'), (b'sublime', b'Sublime text'), (b'emacs', b'Emacs'), (b'vim', b'Vim')]),
        ),
    ]
