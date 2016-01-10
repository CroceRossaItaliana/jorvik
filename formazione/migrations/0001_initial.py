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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('raggio', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Raggio KM')),
                ('locazione', models.ForeignKey(to='base.Locazione', related_name='formazione_aspirante', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True)),
                ('persona', models.OneToOneField(related_name='aspirante', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='AssenzaCorsoBase',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Assenza a Corso Base',
                'verbose_name_plural': 'Assenze ai Corsi Base',
            },
        ),
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('T', 'Terminato'), ('X', 'Annullato')], default='P', verbose_name='Stato')),
                ('data_inizio', models.DateTimeField(help_text='La data di inizio del corso. Utilizzata per la gestione delle iscrizioni.')),
                ('data_esame', models.DateTimeField()),
                ('progressivo', models.SmallIntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(db_index=True)),
                ('descrizione', models.TextField(blank=True, null=True)),
                ('locazione', models.ForeignKey(to='base.Locazione', related_name='formazione_corsobase', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True)),
                ('sede', models.ForeignKey(help_text='La Sede organizzatrice del Corso.', related_query_name='%(class)s_corso', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Corso Base',
                'verbose_name_plural': 'Corsi Base',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='LezioneCorsoBase',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, db_index=True, blank=True, default=None, verbose_name='Fine')),
                ('nome', models.CharField(max_length=128)),
                ('corso', models.ForeignKey(to='formazione.CorsoBase', related_name='lezioni')),
            ],
            options={
                'verbose_name': 'Lezione di Corso Base',
                'verbose_name_plural': 'Lezioni di Corsi Base',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.CreateModel(
            name='PartecipazioneCorsoBase',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, choices=[('A', 'In attesa'), ('C', 'Confermata'), ('N', 'Negata')], default='A', db_index=True)),
                ('corso', models.ForeignKey(to='formazione.CorsoBase', related_name='partecipazioni')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='partecipazioni_corsi')),
            ],
            options={
                'verbose_name': 'Richiesta di partecipazione',
                'verbose_name_plural': 'Richieste di partecipazione',
            },
        ),
        migrations.AddField(
            model_name='assenzacorsobase',
            name='lezione',
            field=models.ForeignKey(to='formazione.LezioneCorsoBase', related_name='assenze'),
        ),
        migrations.AddField(
            model_name='assenzacorsobase',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='assenze_corsi_base'),
        ),
        migrations.AddField(
            model_name='assenzacorsobase',
            name='registrata_da',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='assenze_corsi_base_registrate'),
        ),
    ]
