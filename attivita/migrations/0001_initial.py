# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('vecchio_id', models.IntegerField(default=None, blank=True, null=True, db_index=True)),
                ('nome', models.CharField(max_length=255, default='Nuova attività', db_index=True)),
                ('stato', models.CharField(max_length=1, default='B', db_index=True, choices=[('B', 'Bozza'), ('V', 'Visibile')])),
                ('apertura', models.CharField(max_length=1, default='A', db_index=True, choices=[('C', 'Chiusa'), ('A', 'Aperta')])),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(to='attivita.Area', related_name='attivita')),
                ('estensione', models.ForeignKey(default=None, related_name='attivita_estensione', null=True, to='anagrafica.Sede')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('stato', models.CharField(max_length=1, default='K', db_index=True, choices=[('K', 'Part. Richiesta'), ('X', 'Part. Ritirata'), ('N', 'Non presentato/a')])),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=128, default='Nuovo turno', db_index=True)),
                ('prenotazione', models.DateTimeField(db_index=True, verbose_name='Prenotazione entro')),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, blank=True, null=True, db_index=True, verbose_name='Fine')),
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
