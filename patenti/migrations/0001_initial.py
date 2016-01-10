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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
            ],
            options={
                'verbose_name_plural': 'Elementi patente',
                'verbose_name': 'Elemento patente',
            },
        ),
        migrations.CreateModel(
            name='Patente',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(max_length=2, default='CIV', choices=[('CIV', 'Patente Civile'), ('CRI', 'Patente CRI')])),
            ],
            options={
                'verbose_name_plural': 'Patenti di Guida',
                'verbose_name': 'Patente di Guida',
            },
        ),
    ]
