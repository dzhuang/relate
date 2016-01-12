# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0078_add_image_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionPageImage',
            fields=[
                ('image_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='course.Image')),
                ('image_page_id', models.CharField(max_length=200, null=True, verbose_name='Image Page ID')),
                ('flow_session', models.ForeignKey(related_name='page_image_data', verbose_name='Flow session', to='course.FlowSession', null=True)),
            ],
            bases=('course.image',),
        ),
    ]
