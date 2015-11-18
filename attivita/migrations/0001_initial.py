# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(default='Generale', db_index=True, max_length=256)),
                ('obiettivo', models.SmallIntegerField(default=1, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Aree',
            },
        ),
        migrations.CreateModel(
            name='Attivita',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(default='Nuova attività', db_index=True, max_length=255)),
                ('stato', models.CharField(default='B', db_index=True, max_length=1, choices=[('B', 'Bozza'), ('V', 'Visibile')])),
                ('apertura', models.CharField(default='A', db_index=True, max_length=1, choices=[('C', 'Chiusa'), ('A', 'Aperta')])),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(related_name='attivita', to='attivita.Area')),
                ('estensione', models.ForeignKey(default=None, null=True, related_name='attivita_estensione', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Attività',
                'verbose_name': 'Attività',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.CreateModel(
            name='Partecipazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('stato', models.CharField(default='K', db_index=True, max_length=1, choices=[('K', 'Part. Richiesta'), ('X', 'Part. Ritirata'), ('N', 'Non presentato/a')])),
                ('persona', models.ForeignKey(related_name='partecipazioni', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Richieste di partecipazione',
                'verbose_name': 'Richiesta di partecipazione',
            },
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(default='Nuovo turno', db_index=True, max_length=128)),
                ('prenotazione', models.DateTimeField(db_index=True, verbose_name='Prenotazione entro')),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Fine')),
                ('minimo', models.SmallIntegerField(default=1, db_index=True)),
                ('massimo', models.SmallIntegerField(default=None, db_index=True, null=True)),
                ('attivita', models.ForeignKey(related_name='turni', to='attivita.Attivita')),
            ],
            options={
                'verbose_name_plural': 'Turni',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.AddField(
            model_name='partecipazione',
            name='turno',
            field=models.ForeignKey(related_name='partecipazioni', to='attivita.Turno'),
        ),
    ]
