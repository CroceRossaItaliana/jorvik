# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aspirante',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('raggio', models.FloatField(blank=True, default=0.0, verbose_name='Raggio KM', null=True)),
                ('locazione', models.ForeignKey(related_name='formazione_aspirante', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Locazione', null=True)),
                ('persona', models.OneToOneField(related_name='aspirante', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='AssenzaCorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Assenze ai Corsi Base',
                'verbose_name': 'Assenza a Corso Base',
            },
        ),
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(max_length=1, default='P', choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('T', 'Terminato'), ('X', 'Annullato')], verbose_name='Stato')),
                ('data_inizio', models.DateTimeField(help_text='La data di inizio del corso. Utilizzata per la gestione delle iscrizioni.')),
                ('data_esame', models.DateTimeField()),
                ('progressivo', models.SmallIntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(db_index=True)),
                ('descrizione', models.TextField(blank=True, null=True)),
                ('locazione', models.ForeignKey(related_name='formazione_corsobase', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Locazione', null=True)),
                ('sede', models.ForeignKey(help_text='La Sede organizzatrice del Corso.', related_query_name='%(class)s_corso', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Corsi Base',
                'verbose_name': 'Corso Base',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='LezioneCorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('nome', models.CharField(max_length=128)),
                ('corso', models.ForeignKey(related_name='lezioni', to='formazione.CorsoBase')),
            ],
            options={
                'verbose_name_plural': 'Lezioni di Corsi Base',
                'verbose_name': 'Lezione di Corso Base',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.CreateModel(
            name='PartecipazioneCorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('esito_esame', models.CharField(max_length=2, db_index=True, default=None, choices=[('OK', 'Idoneo'), ('NO', 'Non Idoneo')], null=True)),
                ('ammissione', models.CharField(db_index=True, choices=[('AM', 'Ammesso'), ('NA', 'Non Ammesso'), ('AS', 'Assente')], blank=True, default=None, max_length=2, null=True)),
                ('motivo_non_ammissione', models.CharField(blank=True, max_length=1025, null=True)),
                ('esito_parte_1', models.CharField(help_text='La Croce Rossa', db_index=True, choices=[('P', 'Positivo'), ('N', 'Negativo')], default=None, max_length=1, null=True)),
                ('argomento_parte_1', models.TextField(help_text='es. Storia della CRI, DIU', blank=True, max_length=1024, null=True)),
                ('esito_parte_2', models.CharField(help_text='Gesti e manovre salvavita', db_index=True, choices=[('P', 'Positivo'), ('N', 'Negativo')], default=None, max_length=1, null=True)),
                ('argomento_parte_2', models.TextField(help_text='es. BLS, colpo di calore', blank=True, max_length=1024, null=True)),
                ('extra_1', models.BooleanField(help_text='Prova pratica su Parte 2 sostituita da colloquio.', default=False)),
                ('extra_2', models.BooleanField(help_text='Verifica effettuata solo sulla Parte 1 del programma del corso.', default=False)),
                ('corso', models.ForeignKey(related_name='partecipazioni', to='formazione.CorsoBase')),
                ('persona', models.ForeignKey(related_name='partecipazioni_corsi', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Richieste di partecipazione',
                'verbose_name': 'Richiesta di partecipazione',
            },
        ),
        migrations.AddField(
            model_name='assenzacorsobase',
            name='lezione',
            field=models.ForeignKey(related_name='assenze', to='formazione.LezioneCorsoBase'),
        ),
        migrations.AddField(
            model_name='assenzacorsobase',
            name='persona',
            field=models.ForeignKey(related_name='assenze_corsi_base', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='assenzacorsobase',
            name='registrata_da',
            field=models.ForeignKey(related_name='assenze_corsi_base_registrate', to='anagrafica.Persona'),
        ),
    ]
