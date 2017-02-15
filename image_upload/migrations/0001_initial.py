# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import image_upload.models
import image_upload.storages


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0008_inst_id_unique_and_updates'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.ImageField(storage=image_upload.storages.UserImageStorage(), upload_to=image_upload.storages.user_directory_path)),
                ('slug', models.SlugField(max_length=256, blank=True)),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('id', 'creation_time'),
            },
        ),
        migrations.CreateModel(
            name='SessionPageImage',
            fields=[
                ('image_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='image_upload.Image')),
                ('image_page_id', models.CharField(max_length=200, null=True)),
                ('flow_session', models.ForeignKey(related_name='page_image_data', verbose_name='Flow session', to='course.FlowSession', null=True)),
            ],
            bases=('image_upload.image',),
        ),
        migrations.AddField(
            model_name='image',
            name='creator',
            field=models.ForeignKey(verbose_name='Creator', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
