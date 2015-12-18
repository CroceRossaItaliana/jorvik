# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aspirante',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('raggio', models.FloatField(default=0.0, verbose_name='Raggio KM', blank=True, null=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Assenze ai Corsi Base',
            },
        ),
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')], default='P', verbose_name='Stato', max_length=1)),
                ('data_inizio', models.DateTimeField()),
                ('data_esame', models.DateTimeField()),
                ('locazione', models.ForeignKey(to='base.Locazione', related_name='formazione_corsobase', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede', related_query_name='%(class)s_corso')),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('corso', models.ForeignKey(to='formazione.CorsoBase', related_name='lezioni')),
            ],
            options={
                'verbose_name_plural': 'Lezioni Corsi Base',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='PartecipazioneCorsoBase',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
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
            name='corso',
            field=models.ForeignKey(to='formazione.CorsoBase', related_name='assenze'),
        ),
    ]
