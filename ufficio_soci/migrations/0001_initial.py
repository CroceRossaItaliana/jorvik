# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ufficio_soci.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
            ],
            options={
                'verbose_name': 'Richiesta di Dimissione',
                'verbose_name_plural': 'Richieste di Dimissione',
            },
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('progressivo', models.IntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(default=ufficio_soci.models.Quota.default_anno, db_index=True)),
                ('data_versamento', models.DateField(help_text="La data di versamento dell'importo.")),
                ('data_annullamento', models.DateField(blank=True, null=True)),
                ('stato', models.CharField(max_length=1, choices=[('R', 'Registrata'), ('X', 'Annullata')], default='R', db_index=True)),
                ('importo', models.FloatField()),
                ('importo_extra', models.FloatField(default=0.0)),
                ('causale', models.CharField(max_length=512)),
                ('causale_extra', models.CharField(max_length=512, blank=True)),
                ('annullato_da', models.ForeignKey(to='anagrafica.Persona', related_name='quote_annullate', blank=True, null=True)),
                ('appartenenza', models.ForeignKey(to='anagrafica.Appartenenza', related_name='quote', null=True)),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='quote')),
                ('registrato_da', models.ForeignKey(to='anagrafica.Persona', related_name='quote_registrate')),
                ('sede', models.ForeignKey(to='anagrafica.Sede', related_name='quote')),
            ],
            options={
                'verbose_name_plural': 'Quote',
            },
        ),
        migrations.CreateModel(
            name='Tesseramento',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=1, choices=[('A', 'Aperto'), ('C', 'Chiuso')], default='A')),
                ('anno', models.SmallIntegerField(unique=True, default=ufficio_soci.models.Tesseramento.default_anno, db_index=True)),
                ('inizio', models.DateField(default=ufficio_soci.models.Tesseramento.default_inizio, db_index=True)),
                ('quota_attivo', models.FloatField(default=8.0)),
                ('quota_ordinario', models.FloatField(default=16.0)),
                ('quota_benemerito', models.FloatField(default=20.0)),
                ('quota_aspirante', models.FloatField(default=20.0)),
            ],
            options={
                'verbose_name': 'Tesseramento',
                'verbose_name_plural': 'Tesseramenti',
            },
        ),
        migrations.CreateModel(
            name='Tesserino',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
            ],
            options={
                'verbose_name': 'Richiesta Tesserino Associativo',
                'verbose_name_plural': 'Richieste Tesserino Associativo',
            },
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('progressivo', 'anno', 'sede')]),
        ),
    ]
