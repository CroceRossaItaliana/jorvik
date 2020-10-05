# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-10-05 15:16
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import social.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0021_auto_20201005_1516'),
        ('anagrafica', '0064_auto_20201005_1516'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatoreLavoro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nominativo', models.CharField(blank=True, db_index=True, default='', max_length=25, null=True)),
                ('ragione_sociale', models.CharField(blank=True, db_index=True, default='', max_length=25, null=True)),
                ('partita_iva', models.CharField(blank=True, db_index=True, default='', max_length=11, null=True)),
                ('telefono', models.CharField(blank=True, db_index=True, default='', max_length=10, null=True)),
                ('referente', models.CharField(blank=True, db_index=True, default='', max_length=25, null=True)),
                ('email', models.CharField(blank=True, db_index=True, default='', max_length=25, null=True)),
                ('pec', models.CharField(blank=True, db_index=True, default='', max_length=25, null=True)),
                ('persona', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Datore di lavoro',
                'verbose_name_plural': 'Datori di lavoro',
            },
        ),
        migrations.CreateModel(
            name='MezzoSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(choices=[('me', 'Mezzo'), ('ma', 'Materiale')], max_length=3)),
                ('mezzo_tipo', models.CharField(blank=True, choices=[('m1', 'Mezzo CRI'), ('m2', 'Mezzo in leasing')], max_length=3, null=True)),
                ('nome', models.CharField(max_length=255, verbose_name='Nome')),
                ('stato', models.CharField(choices=[('is', 'In servizio'), ('dm', 'Dimesso'), ('fu', 'Fuori servizio')], default='is', max_length=2)),
                ('creato_da', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='anagrafica.Persona')),
                ('estensione', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='mezzo_materiale_estensione', to='anagrafica.Sede', verbose_name='Collocazione')),
            ],
            options={
                'verbose_name': 'Mezzo o materiale',
                'verbose_name_plural': 'Mezzi e materiali',
            },
        ),
        migrations.CreateModel(
            name='PartecipazioneSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='Fine')),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('automatica', models.BooleanField(db_index=True, default=False, verbose_name='Automatica')),
                ('stato', models.CharField(choices=[('p', 'Partecipa'), ('r', 'Ritirato')], db_index=True, default='p', max_length=1)),
            ],
            options={
                'verbose_name': 'Partecipazione al Turno di un Servizio SO',
                'verbose_name_plural': 'Partecipazioni ai Turni dei Servizi SO',
                'permissions': (('view_partecipazione', 'Can view partecipazione'),),
            },
        ),
        migrations.CreateModel(
            name='PrenotazioneMMSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='Fine')),
                ('mezzo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sala_operativa.MezzoSO')),
            ],
            options={
                'verbose_name': 'Prenotazione Mezzo o materiale',
                'verbose_name_plural': 'Prenotazione Mezzi e materiali',
            },
        ),
        migrations.CreateModel(
            name='ReperibilitaSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='Fine')),
                ('attivazione', models.TimeField(default='00:15', help_text="Tempo necessario all'attivazione, in formato HH:mm.", verbose_name='Tempo di attivazione')),
                ('estensione', models.CharField(choices=[('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], max_length=2)),
                ('applicazione_bdl', models.BooleanField(default=False, verbose_name='Applicazione dei Benefici di Legge')),
                ('creato_da', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='anagrafica.Persona')),
                ('datore_lavoro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sala_operativa.DatoreLavoro')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='so_reperibilita', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Reperibilità',
                'verbose_name': 'Reperibilità',
                'ordering': ['-inizio', '-fine'],
                'permissions': (('view_reperibilita', 'Can view Reperibilità'),),
            },
        ),
        migrations.CreateModel(
            name='ServizioSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='Fine')),
                ('nome', models.CharField(db_index=True, default='Nuovo servizio', max_length=255)),
                ('stato', models.CharField(choices=[('B', 'Bozza'), ('V', 'Visibile')], db_index=True, default='B', max_length=1)),
                ('apertura', models.CharField(choices=[('C', 'Chiuso'), ('A', 'Aperto')], db_index=True, default='A', max_length=1)),
                ('impiego_bdl', models.BooleanField(default=False, verbose_name="L'attività prevede l'impiego dei Benefici di Legge")),
                ('descrizione', models.TextField(blank=True)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('estensione', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='servizio_estensione', to='anagrafica.Sede')),
                ('locazione', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sala_operativa_servizioso', to='base.Locazione')),
                ('sede', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='servizio', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Servizio',
                'verbose_name_plural': 'Servizi',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.CreateModel(
            name='TurnoSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(db_index=True, default='Nuovo turno', max_length=128)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Data e ora di inizio')),
                ('fine', models.DateTimeField(blank=True, db_index=True, default=None, null=True, verbose_name='Data e ora di fine')),
                ('minimo', models.SmallIntegerField(db_index=True, default=1, verbose_name='Num. minimo di partecipanti')),
                ('massimo', models.SmallIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='Num. massimo di partecipanti')),
                ('attivita', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turni_so', to='sala_operativa.ServizioSO')),
            ],
            options={
                'verbose_name_plural': 'Turni dei Servizi',
                'verbose_name': 'Turno di Servizio',
                'ordering': ['inizio', 'fine', 'id'],
                'permissions': (('view_turno', 'Can view turno'),),
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.AddField(
            model_name='prenotazionemmso',
            name='servizio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sala_operativa.ServizioSO'),
        ),
        migrations.AddField(
            model_name='partecipazioneso',
            name='reperibilita',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sala_operativa.ReperibilitaSO'),
        ),
        migrations.AddField(
            model_name='partecipazioneso',
            name='turno',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partecipazioni_so', to='sala_operativa.TurnoSO'),
        ),
        migrations.AlterIndexTogether(
            name='turnoso',
            index_together=set([('attivita', 'inizio', 'fine'), ('inizio', 'fine'), ('attivita', 'inizio')]),
        ),
        migrations.AlterIndexTogether(
            name='partecipazioneso',
            index_together=set([('reperibilita', 'turno'), ('reperibilita', 'turno', 'stato'), ('turno', 'stato')]),
        ),
    ]
