# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import course.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0081_course_fields_i18n'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.ImageField(storage=course.models.UserImageStorage(), upload_to=course.models.user_directory_path)),
                ('slug', models.SlugField(max_length=256, blank=True)),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('id', 'creation_time'),
            },
        ),
        migrations.AddField(
            model_name='course',
            name='enroll_deadline',
            field=models.DateField(help_text="After which the course will not be displayed on home page, and enrollment will not be allowed. Leave this field blank if there's no deadline of enrollment.", null=True, verbose_name='Enrollment deadline', blank=True),
        ),
        migrations.CreateModel(
            name='SessionPageImage',
            fields=[
                ('image_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='course.Image')),
                ('image_page_id', models.CharField(max_length=200, null=True, verbose_name='Image Page ID')),
                ('flow_session', models.ForeignKey(related_name='page_image_data', verbose_name='Flow session', to='course.FlowSession', null=True)),
            ],
            bases=('course.image',),
        ),
        migrations.AddField(
            model_name='image',
            name='creator',
            field=models.ForeignKey(verbose_name='Creator', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
