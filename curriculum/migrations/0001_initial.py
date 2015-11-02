# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151102_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competenza',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
                'verbose_name': 'Competenza CRI',
                'verbose_name_plural': 'Competenze CRI',
            },
        ),
        migrations.CreateModel(
            name='CompetenzaPersonale',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('competenza', models.ForeignKey(to='curriculum.Competenza')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='competenze_personali')),
            ],
            options={
                'verbose_name': 'Competenza personale',
                'verbose_name_plural': 'Competenze personali',
            },
        ),
        migrations.CreateModel(
            name='Titolo',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
                'verbose_name_plural': 'Titoli',
            },
        ),
        migrations.CreateModel(
            name='TitoloPersonale',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='titoli_personali')),
                ('titolo', models.ForeignKey(to='curriculum.Titolo')),
            ],
            options={
                'verbose_name': 'Titolo personale',
                'verbose_name_plural': 'Titoli personali',
            },
        ),
    ]
