# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('raggio', models.FloatField(null=True, blank=True, verbose_name='Raggio KM', default=0.0)),
                ('locazione', models.ForeignKey(blank=True, related_name='formazione_aspirante', to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('persona', models.OneToOneField(to='anagrafica.Persona', related_name='aspirante')),
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
            },
        ),
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')], max_length=1, verbose_name='Stato', default='P')),
                ('data_inizio', models.DateTimeField()),
                ('data_esame', models.DateTimeField()),
                ('locazione', models.ForeignKey(blank=True, related_name='formazione_corsobase', to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('sede', models.ForeignKey(related_query_name='%(class)s_corso', to='anagrafica.Sede')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
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
