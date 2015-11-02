# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0002_auto_20151102_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, default='Generale', max_length=256)),
                ('obiettivo', models.SmallIntegerField(db_index=True, default=1)),
                ('sede', models.ForeignKey(related_name='aree', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Aree',
            },
        ),
        migrations.CreateModel(
            name='Attivita',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, default='Nuova attività', max_length=255)),
                ('stato', models.CharField(db_index=True, choices=[('B', 'Bozza'), ('V', 'Visibile')], default='B', max_length=1)),
                ('apertura', models.CharField(db_index=True, choices=[('C', 'Chiusa'), ('A', 'Aperta')], default='A', max_length=1)),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(related_name='attivita', to='attivita.Area')),
                ('estensione', models.ForeignKey(related_name='attivita_estensione', default=None, null=True, to='anagrafica.Sede')),
                ('locazione', models.ForeignKey(related_name='attivita_attivita', null=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, blank=True)),
                ('sede', models.ForeignKey(related_name='attivita', to='anagrafica.Sede')),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('stato', models.CharField(db_index=True, choices=[('K', 'Part. Richiesta'), ('X', 'Part. Ritirata'), ('N', 'Non presentato/a')], default='K', max_length=1)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, default='Nuovo turno', max_length=128)),
                ('prenotazione', models.DateTimeField(db_index=True, verbose_name='Prenotazione entro')),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(db_index=True, blank=True, verbose_name='Fine', default=None, null=True)),
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
