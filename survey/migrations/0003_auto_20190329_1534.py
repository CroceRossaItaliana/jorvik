# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-03-29 15:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_surveyresult_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='question_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.QuestionGroup'),
        ),
    ]
