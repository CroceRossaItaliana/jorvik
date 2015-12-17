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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=256, default='Generale', db_index=True)),
                ('obiettivo', models.SmallIntegerField(default=1, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Aree',
            },
        ),
        migrations.CreateModel(
            name='Attivita',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=255, default='Nuova attività', db_index=True)),
                ('stato', models.CharField(max_length=1, default='B', db_index=True, choices=[('B', 'Bozza'), ('V', 'Visibile')])),
                ('apertura', models.CharField(max_length=1, default='A', db_index=True, choices=[('C', 'Chiusa'), ('A', 'Aperta')])),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(related_name='attivita', to='attivita.Area')),
                ('estensione', models.ForeignKey(null=True, default=None, related_name='attivita_estensione', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Attività',
                'verbose_name_plural': 'Attività',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.CreateModel(
            name='Partecipazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('stato', models.CharField(max_length=1, default='K', db_index=True, choices=[('K', 'Part. Richiesta'), ('X', 'Part. Ritirata'), ('N', 'Non presentato/a')])),
                ('persona', models.ForeignKey(related_name='partecipazioni', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Richiesta di partecipazione',
                'verbose_name_plural': 'Richieste di partecipazione',
            },
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=128, default='Nuovo turno', db_index=True)),
                ('prenotazione', models.DateTimeField(verbose_name='Prenotazione entro', db_index=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(null=True, verbose_name='Fine', default=None, blank=True, db_index=True)),
                ('minimo', models.SmallIntegerField(default=1, db_index=True)),
                ('massimo', models.SmallIntegerField(null=True, default=None, db_index=True)),
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
