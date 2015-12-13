# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151213_1443'),
        ('base', '0002_auto_20151204_2015'),
        ('formazione', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorsoBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, default='P', choices=[('P', 'In preparazione'), ('A', 'Attivo'), ('I', 'Iniziato'), ('T', 'Terminato'), ('A', 'Annullato')], verbose_name='Stato')),
                ('data_inizio', models.DateTimeField()),
                ('data_esame', models.DateTimeField()),
                ('locazione', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='base.Locazione', null=True, related_name='formazione_corsobase', blank=True)),
                ('sede', models.ForeignKey(related_query_name='%(class)s_corso', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Corsi Base',
                'verbose_name': 'Corso Base',
            },
            bases=(models.Model, social.models.ConGiudizio),
        ),
        migrations.CreateModel(
            name='PartecipazioneCorsoBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
                ('corso', models.ForeignKey(related_name='partecipazioni', to='formazione.CorsoBase')),
                ('persona', models.ForeignKey(related_name='partecipazioni_corsi', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Richieste di partecipazione',
                'verbose_name': 'Richiesta di partecipazione',
            },
        ),
        migrations.RenameModel(
            old_name='Assenza',
            new_name='AssenzaCorsoBase',
        ),
        migrations.RenameModel(
            old_name='Lezione',
            new_name='LezioneCorsoBase',
        ),
        migrations.RemoveField(
            model_name='corso',
            name='locazione',
        ),
        migrations.RemoveField(
            model_name='corso',
            name='sede',
        ),
        migrations.RemoveField(
            model_name='partecipazione',
            name='corso',
        ),
        migrations.RemoveField(
            model_name='partecipazione',
            name='persona',
        ),
        migrations.AlterModelOptions(
            name='assenzacorsobase',
            options={'verbose_name_plural': 'Assenze ai Corsi Base'},
        ),
        migrations.AlterModelOptions(
            name='lezionecorsobase',
            options={'verbose_name_plural': 'Lezioni Corsi Base'},
        ),
        migrations.AlterField(
            model_name='assenzacorsobase',
            name='corso',
            field=models.ForeignKey(related_name='assenze', to='formazione.CorsoBase'),
        ),
        migrations.AlterField(
            model_name='lezionecorsobase',
            name='corso',
            field=models.ForeignKey(related_name='lezioni', to='formazione.CorsoBase'),
        ),
        migrations.DeleteModel(
            name='Corso',
        ),
        migrations.DeleteModel(
            name='Partecipazione',
        ),
    ]
