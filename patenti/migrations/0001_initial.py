# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


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
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
            ],
            options={
                'verbose_name': 'Elemento patente',
                'verbose_name_plural': 'Elementi patente',
            },
        ),
        migrations.CreateModel(
            name='Patente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(default='CIV', choices=[('CIV', 'Patente Civile'), ('CRI', 'Patente CRI')], max_length=2)),
            ],
            options={
                'verbose_name': 'Patente di Guida',
                'verbose_name_plural': 'Patenti di Guida',
            },
        ),
    ]
