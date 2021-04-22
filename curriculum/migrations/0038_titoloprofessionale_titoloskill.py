# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-03-17 15:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0037_auto_20210317_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='TitoloProfessionale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('titolo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curriculum.Titolo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TitoloSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('titolo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curriculum.Titolo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
