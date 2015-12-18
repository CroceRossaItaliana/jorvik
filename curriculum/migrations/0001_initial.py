# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competenza',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name_plural': 'Competenze CRI',
                'verbose_name': 'Competenza CRI',
            },
        ),
        migrations.CreateModel(
            name='CompetenzaPersonale',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('competenza', models.ForeignKey(to='curriculum.Competenza')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='competenze_personali')),
            ],
            options={
                'verbose_name_plural': 'Competenze personali',
                'verbose_name': 'Competenza personale',
            },
        ),
        migrations.CreateModel(
            name='Titolo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name_plural': 'Titoli',
            },
        ),
        migrations.CreateModel(
            name='TitoloPersonale',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='titoli_personali')),
                ('titolo', models.ForeignKey(to='curriculum.Titolo')),
            ],
            options={
                'verbose_name_plural': 'Titoli personali',
                'verbose_name': 'Titolo personale',
            },
        ),
    ]
