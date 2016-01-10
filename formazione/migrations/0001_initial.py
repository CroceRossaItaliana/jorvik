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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('raggio', models.FloatField(default=0.0, blank=True, null=True, verbose_name='Raggio KM')),
                ('locazione', models.ForeignKey(to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, related_name='formazione_aspirante', null=True, blank=True)),
                ('persona', models.OneToOneField(to='anagrafica.Persona', related_name='aspirante')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='AssenzaCorsoBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'verbose_name': 'Assenza a Corso Base',
                'verbose_name_plural': 'Assenze ai Corsi Base',
            },
        ),
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(default='P', choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('T', 'Terminato'), ('X', 'Annullato')], verbose_name='Stato', max_length=1)),
                ('data_inizio', models.DateTimeField(help_text='La data di inizio del corso. Utilizzata per la gestione delle iscrizioni.')),
                ('data_esame', models.DateTimeField()),
                ('progressivo', models.SmallIntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(db_index=True)),
                ('descrizione', models.TextField(blank=True, null=True)),
                ('locazione', models.ForeignKey(to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, related_name='formazione_corsobase', null=True, blank=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede', help_text='La Sede organizzatrice del Corso.', related_query_name='%(class)s_corso')),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, null=True, db_index=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', verbose_name='Fine', blank=True)),
                ('nome', models.CharField(max_length=128)),
                ('corso', models.ForeignKey(related_name='lezioni', to='formazione.CorsoBase')),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(db_index=True, default='A', choices=[('A', 'In attesa'), ('C', 'Confermata'), ('N', 'Negata')], max_length=1)),
                ('corso', models.ForeignKey(related_name='partecipazioni', to='formazione.CorsoBase')),
                ('persona', models.ForeignKey(related_name='partecipazioni_corsi', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Richiesta di partecipazione',
                'verbose_name_plural': 'Richieste di partecipazione',
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
