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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
            ],
            options={
                'verbose_name': 'Elemento patente',
                'verbose_name_plural': 'Elementi patente',
            },
        ),
        migrations.CreateModel(
            name='Patente',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(max_length=2, default='CIV', choices=[('CIV', 'Patente Civile'), ('CRI', 'Patente CRI')])),
            ],
            options={
                'verbose_name': 'Patente di Guida',
                'verbose_name_plural': 'Patenti di Guida',
            },
        ),
    ]
