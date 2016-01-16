# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gruppi.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('attivita', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('motivo_negazione', models.CharField(blank=True, max_length=512, null=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Gruppo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('estensione', models.CharField(max_length=1, db_index=True, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome')),
                ('obiettivo', models.IntegerField(db_index=True, validators=[gruppi.models.tra_1_e_6])),
                ('area', models.ForeignKey(related_name='gruppi', to='attivita.Area')),
                ('attivita', models.ForeignKey(related_name='gruppi', to='attivita.Attivita', null=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Gruppi',
            },
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='gruppo',
            field=models.ForeignKey(related_name='appartenenze', to='gruppi.Gruppo'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='negato_da',
            field=models.ForeignKey(related_name='appartenenze_gruppi_negate', to='anagrafica.Persona', null=True),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(related_name='appartenenze_gruppi', to='anagrafica.Persona'),
        ),
    ]
