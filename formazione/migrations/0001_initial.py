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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('raggio', models.FloatField(blank=True, verbose_name='Raggio KM', default=0.0, null=True)),
                ('locazione', models.ForeignKey(related_name='formazione_aspirante', to='base.Locazione', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('persona', models.OneToOneField(related_name='aspirante', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='Assenza',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Assenze',
            },
        ),
        migrations.CreateModel(
            name='Corso',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(choices=[('BA', 'Corso Base')], verbose_name='Tipo', max_length=2, default='BA')),
                ('stato', models.CharField(choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')], verbose_name='Stato', max_length=1, default='P')),
                ('locazione', models.ForeignKey(related_name='formazione_corso', to='base.Locazione', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('sede', models.ForeignKey(related_name='corsi', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Corso di formazione',
                'verbose_name_plural': 'Corsi di formazione',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='Lezione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('corso', models.ForeignKey(related_name='lezioni', to='formazione.Corso')),
            ],
            options={
                'verbose_name_plural': 'Lezioni',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='Partecipazione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
                ('corso', models.ForeignKey(related_name='partecipazioni', to='formazione.Corso')),
                ('persona', models.ForeignKey(related_name='partecipazioni_corsi', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Richiesta di partecipazione',
                'verbose_name_plural': 'Richieste di partecipazione',
            },
        ),
        migrations.AddField(
            model_name='assenza',
            name='corso',
            field=models.ForeignKey(related_name='assenze', to='formazione.Corso'),
        ),
    ]
