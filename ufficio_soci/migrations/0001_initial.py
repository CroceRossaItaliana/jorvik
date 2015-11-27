# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Richiesta di Dimissione',
                'verbose_name_plural': 'Richieste di Dimissione',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Richiesta di Estensione',
                'verbose_name_plural': 'Richieste di Estensione',
            },
        ),
        migrations.CreateModel(
            name='Tesserino',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Richiesta Tesserino Associativo',
                'verbose_name_plural': 'Richieste Tesserino Associativo',
            },
        ),
        migrations.CreateModel(
            name='Trasferimento',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Richiesta di Trasferimento',
                'verbose_name_plural': 'Richieste di Trasferimento',
            },
        ),
    ]
