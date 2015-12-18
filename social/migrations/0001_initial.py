# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151218_1609'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commento',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('commento', models.TextField(verbose_name='Testo del commento')),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='commenti')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'Commenti',
            },
        ),
        migrations.CreateModel(
            name='Giudizio',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('positivo', models.BooleanField(default=True, verbose_name='Positivo', db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='giudizi')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Giudizi',
            },
        ),
    ]
