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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('raggio', models.FloatField(null=True, verbose_name='Raggio KM', default=0.0, blank=True)),
                ('locazione', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='formazione_aspirante', to='base.Locazione')),
                ('persona', models.OneToOneField(related_name='aspirante', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Aspiranti',
            },
        ),
        migrations.CreateModel(
            name='AssenzaCorsoBase',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, verbose_name='Stato', default='P', choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')])),
                ('data_inizio', models.DateTimeField()),
                ('data_esame', models.DateTimeField()),
                ('locazione', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='formazione_corsobase', to='base.Locazione')),
                ('sede', models.ForeignKey(related_query_name='%(class)s_corso', to='anagrafica.Sede')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('corso', models.ForeignKey(related_name='lezioni', to='formazione.CorsoBase')),
            ],
            options={
                'verbose_name_plural': 'Lezioni Corsi Base',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='PartecipazioneCorsoBase',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
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
            name='corso',
            field=models.ForeignKey(related_name='assenze', to='formazione.CorsoBase'),
        ),
    ]
