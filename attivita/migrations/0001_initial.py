# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '__first__'),
        ('base', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(default='Generale', db_index=True, max_length=256)),
                ('obiettivo', models.SmallIntegerField(default=1, db_index=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede', related_name='aree')),
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
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(default='Nuova attività', db_index=True, max_length=255)),
                ('stato', models.CharField(choices=[('B', 'Bozza'), ('V', 'Visibile')], default='B', db_index=True, max_length=1)),
                ('apertura', models.CharField(choices=[('C', 'Chiusa'), ('A', 'Aperta')], default='A', db_index=True, max_length=1)),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(to='attivita.Area', related_name='attivita')),
                ('estensione', models.ForeignKey(to='anagrafica.Sede', null=True, related_name='attivita_estensione', default=None)),
                ('locazione', models.ForeignKey(blank=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='attivita_attivita')),
                ('sede', models.ForeignKey(to='anagrafica.Sede', related_name='attivita')),
            ],
            options={
                'verbose_name_plural': 'Attività',
                'verbose_name': 'Attività',
            },
            bases=(social.models.ConGiudizio, social.models.ConCommenti, models.Model),
        ),
        migrations.CreateModel(
            name='Partecipazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='partecipazioni')),
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
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(default='Nuovo turno', db_index=True, max_length=128)),
                ('prenotazione', models.DateTimeField(db_index=True, verbose_name='Prenotazione entro')),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(blank=True, default=None, db_index=True, verbose_name='Fine', null=True)),
                ('minimo', models.SmallIntegerField(default=1, db_index=True)),
                ('massimo', models.SmallIntegerField(default=None, db_index=True, null=True)),
                ('attivita', models.ForeignKey(to='attivita.Attivita', related_name='turni')),
            ],
            options={
                'verbose_name_plural': 'Turni',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.AddField(
            model_name='partecipazione',
            name='turno',
            field=models.ForeignKey(to='attivita.Turno', related_name='partecipazioni'),
        ),
    ]
