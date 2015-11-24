# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151124_1757'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commento',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('commento', models.TextField(verbose_name='Testo del commento')),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(related_name='commenti', to='anagrafica.Persona')),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('positivo', models.BooleanField(verbose_name='Positivo', db_index=True, default=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(related_name='giudizi', to='anagrafica.Persona')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Giudizi',
            },
        ),
    ]
