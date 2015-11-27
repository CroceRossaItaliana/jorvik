# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Elemento',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Elemento patente',
                'verbose_name_plural': 'Elementi patente',
            },
        ),
        migrations.CreateModel(
            name='Patente',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(choices=[('CIV', 'Patente Civile'), ('CRI', 'Patente CRI')], max_length=2, default='CIV')),
            ],
            options={
                'verbose_name': 'Patente di Guida',
                'verbose_name_plural': 'Patenti di Guida',
            },
        ),
    ]
