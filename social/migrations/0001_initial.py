# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('anagrafica', '0002_auto_20151214_1326'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commento',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('commento', models.TextField(verbose_name='Testo del commento')),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(related_name='commenti', to='anagrafica.Persona')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Commenti',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Giudizio',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('positivo', models.BooleanField(verbose_name='Positivo', default=True, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(related_name='giudizi', to='anagrafica.Persona')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Giudizi',
            },
        ),
    ]
