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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
            ],
            options={
                'verbose_name_plural': 'Elementi patente',
                'verbose_name': 'Elemento patente',
            },
        ),
        migrations.CreateModel(
            name='Patente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(choices=[('CIV', 'Patente Civile'), ('CRI', 'Patente CRI')], max_length=2, default='CIV')),
            ],
            options={
                'verbose_name_plural': 'Patenti di Guida',
                'verbose_name': 'Patente di Guida',
            },
        ),
    ]
