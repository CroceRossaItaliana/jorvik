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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(max_length=256, db_index=True, default='Generale')),
                ('obiettivo', models.SmallIntegerField(db_index=True, default=1)),
            ],
            options={
                'verbose_name_plural': 'Aree',
            },
        ),
        migrations.CreateModel(
            name='Attivita',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(max_length=255, db_index=True, default='Nuova attività')),
                ('stato', models.CharField(choices=[('B', 'Bozza'), ('V', 'Visibile')], max_length=1, db_index=True, default='B')),
                ('apertura', models.CharField(choices=[('C', 'Chiusa'), ('A', 'Aperta')], max_length=1, db_index=True, default='A')),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(related_name='attivita', to='attivita.Area')),
                ('estensione', models.ForeignKey(to='anagrafica.Sede', null=True, related_name='attivita_estensione', default=None)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
                ('stato', models.CharField(choices=[('K', 'Part. Richiesta'), ('X', 'Part. Ritirata'), ('N', 'Non presentato/a')], max_length=1, db_index=True, default='K')),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(max_length=128, db_index=True, default='Nuovo turno')),
                ('prenotazione', models.DateTimeField(verbose_name='Prenotazione entro', db_index=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(blank=True, verbose_name='Fine', db_index=True, default=None, null=True)),
                ('minimo', models.SmallIntegerField(db_index=True, default=1)),
                ('massimo', models.SmallIntegerField(db_index=True, default=None, null=True)),
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
