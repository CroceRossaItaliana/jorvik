# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aspirante',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('raggio', models.FloatField(null=True, verbose_name='Raggio KM', default=0.0, blank=True)),
                ('locazione', models.ForeignKey(null=True, blank=True, related_name='formazione_aspirante', to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL)),
                ('persona', models.OneToOneField(to='anagrafica.Persona', related_name='aspirante')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='Assenza',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Assenze',
            },
        ),
        migrations.CreateModel(
            name='Corso',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(choices=[('BA', 'Corso Base')], verbose_name='Tipo', default='BA', max_length=2)),
                ('stato', models.CharField(choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')], verbose_name='Stato', default='P', max_length=1)),
                ('locazione', models.ForeignKey(null=True, blank=True, related_name='formazione_corso', to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL)),
                ('sede', models.ForeignKey(to='anagrafica.Sede', related_name='corsi')),
            ],
            options={
                'verbose_name': 'Corso di formazione',
                'verbose_name_plural': 'Corsi di formazione',
            },
            bases=(models.Model, social.models.ConCommenti, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='Lezione',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('corso', models.ForeignKey(to='formazione.Corso', related_name='lezioni')),
            ],
            options={
                'verbose_name_plural': 'Lezioni',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='Partecipazione',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('corso', models.ForeignKey(to='formazione.Corso', related_name='partecipazioni')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='partecipazioni_corsi')),
            ],
            options={
                'verbose_name': 'Richiesta di partecipazione',
                'verbose_name_plural': 'Richieste di partecipazione',
            },
        ),
        migrations.AddField(
            model_name='assenza',
            name='corso',
            field=models.ForeignKey(to='formazione.Corso', related_name='assenze'),
        ),
    ]
