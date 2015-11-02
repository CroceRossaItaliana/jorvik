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
            name='Aspirante',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('raggio', models.FloatField(blank=True, verbose_name='Raggio KM', null=True, default=0.0)),
                ('locazione', models.ForeignKey(related_name='formazione_aspirante', blank=True, to='base.Locazione', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('persona', models.OneToOneField(to='anagrafica.Persona', related_name='aspirante')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='Assenza',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(choices=[('BA', 'Corso Base')], verbose_name='Tipo', max_length=2, default='BA')),
                ('stato', models.CharField(choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')], verbose_name='Stato', max_length=1, default='P')),
                ('locazione', models.ForeignKey(related_name='formazione_corso', blank=True, to='base.Locazione', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('sede', models.ForeignKey(to='anagrafica.Sede', related_name='corsi')),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
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
