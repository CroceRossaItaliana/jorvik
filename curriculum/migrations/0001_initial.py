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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Competenze CRI',
                'verbose_name': 'Competenza CRI',
            },
        ),
        migrations.CreateModel(
            name='CompetenzaPersonale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('competenza', models.ForeignKey(to='curriculum.Competenza')),
                ('persona', models.ForeignKey(related_name='competenze_personali', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Competenze personali',
                'verbose_name': 'Competenza personale',
            },
        ),
        migrations.CreateModel(
            name='Titolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Titoli',
            },
        ),
        migrations.CreateModel(
            name='TitoloPersonale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('persona', models.ForeignKey(related_name='titoli_personali', to='anagrafica.Persona')),
                ('titolo', models.ForeignKey(to='curriculum.Titolo')),
            ],
            options={
                'verbose_name_plural': 'Titoli personali',
                'verbose_name': 'Titolo personale',
            },
        ),
    ]
