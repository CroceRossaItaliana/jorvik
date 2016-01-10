# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aspirante',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('raggio', models.FloatField(default=0.0, blank=True, null=True, verbose_name='Raggio KM')),
                ('locazione', models.ForeignKey(blank=True, related_name='formazione_aspirante', null=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL)),
                ('persona', models.OneToOneField(related_name='aspirante', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='AssenzaCorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Assenze ai Corsi Base',
                'verbose_name': 'Assenza a Corso Base',
            },
        ),
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, default='P', choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('T', 'Terminato'), ('X', 'Annullato')], verbose_name='Stato')),
                ('data_inizio', models.DateTimeField(help_text='La data di inizio del corso. Utilizzata per la gestione delle iscrizioni.')),
                ('data_esame', models.DateTimeField()),
                ('progressivo', models.SmallIntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(db_index=True)),
                ('descrizione', models.TextField(blank=True, null=True)),
                ('locazione', models.ForeignKey(blank=True, related_name='formazione_corsobase', null=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL)),
                ('sede', models.ForeignKey(related_query_name='%(class)s_corso', help_text='La Sede organizzatrice del Corso.', to='anagrafica.Sede')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, blank=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, verbose_name='Fine', db_index=True)),
                ('nome', models.CharField(max_length=128)),
                ('corso', models.ForeignKey(to='formazione.CorsoBase', related_name='lezioni')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, default='A', db_index=True, choices=[('A', 'In attesa'), ('C', 'Confermata'), ('N', 'Negata')])),
                ('corso', models.ForeignKey(to='formazione.CorsoBase', related_name='partecipazioni')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='partecipazioni_corsi')),
            ],
            options={
                'verbose_name_plural': 'Richieste di partecipazione',
                'verbose_name': 'Richiesta di partecipazione',
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
