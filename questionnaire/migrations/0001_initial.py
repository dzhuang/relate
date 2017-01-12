# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 08:01
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', jsonfield.fields.JSONField(blank=True, help_text='The text answer related to the question', verbose_name='Answer')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Date')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200, verbose_name='Text choice')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Note: Title of question', max_length=100, verbose_name='Title Question')),
                ('required', models.BooleanField(default=False, help_text='The users are required to answer', verbose_name='Question Required')),
                ('type', models.CharField(choices=[('yesNoQuestion', '<span class="black-text">Yes/No</span><br><small class="teal-text">The participant must respond with Yes or No.</small>'), ('MultiChoices', '<span class="black-text">Multiple choices with one Answer</span><br><small class="teal-text">The participant is conducted to pick one in response options list.</small>'), ('MultiChoiceWithAnswer', '<span class="black-text">Multiple choices with multiple answers</span><br><small class="teal-text">The participant is conducted to pick (one or more responses) in response options list.</small>'), ('MutuallyExclusiveField', '<span class="black-text">Question with multually exclusive answers</span><br><small class="teal-text">The participant is conducted to pick (one or more responses) in response options list.</small>'), ('TextField', '<span class="black-text">评论区</span><br><small class="teal-text">Use the comment box to collect written comments from respondents.</small>'), ('RatingField', '<span class="black-text">Rating scale</span><br><small class="teal-text">The respondents will rate the level of satisfaction.</small>')], default='yesNoQuestion', max_length=200, verbose_name='Type of answer')),
                ('order', models.IntegerField(default=0, verbose_name='order')),
                ('help_text', models.TextField(blank=True, verbose_name='Help Text')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Note: Name of the questionnaires', max_length=200, verbose_name='Questionnaire title')),
                ('description', models.TextField(blank=True, help_text='Enter the text that presents the questionnaire', verbose_name='Description')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Questionnaire'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(help_text='The question that this is an answer to', on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(help_text='The user who supplied this answer', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('user', 'question')]),
        ),
    ]
