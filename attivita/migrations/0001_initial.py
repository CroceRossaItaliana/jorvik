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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, default='Generale', max_length=256)),
                ('obiettivo', models.SmallIntegerField(db_index=True, default=1)),
            ],
            options={
                'verbose_name_plural': 'Aree',
            },
        ),
        migrations.CreateModel(
            name='Attivita',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('vecchio_id', models.IntegerField(db_index=True, default=None, blank=True, null=True)),
                ('nome', models.CharField(db_index=True, default='Nuova attività', max_length=255)),
                ('stato', models.CharField(db_index=True, default='B', choices=[('B', 'Bozza'), ('V', 'Visibile')], max_length=1)),
                ('apertura', models.CharField(db_index=True, default='A', choices=[('C', 'Chiusa'), ('A', 'Aperta')], max_length=1)),
                ('descrizione', models.TextField(blank=True)),
                ('area', models.ForeignKey(related_name='attivita', to='attivita.Area')),
                ('estensione', models.ForeignKey(to='anagrafica.Sede', default=None, related_name='attivita_estensione', null=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('stato', models.CharField(db_index=True, default='K', choices=[('K', 'Part. Richiesta'), ('X', 'Part. Ritirata'), ('N', 'Non presentato/a')], max_length=1)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, default='Nuovo turno', max_length=128)),
                ('prenotazione', models.DateTimeField(db_index=True, verbose_name='Prenotazione entro')),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(db_index=True, default=None, blank=True, null=True, verbose_name='Fine')),
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
