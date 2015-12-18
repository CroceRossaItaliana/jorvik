# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151218_1152'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commento',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('commento', models.TextField(verbose_name='Testo del commento')),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='commenti')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('positivo', models.BooleanField(db_index=True, verbose_name='Positivo', default=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='giudizi')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Giudizi',
            },
        ),
    ]
