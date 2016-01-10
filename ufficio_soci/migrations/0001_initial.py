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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
            ],
            options={
                'verbose_name': 'Richiesta di Dimissione',
                'verbose_name_plural': 'Richieste di Dimissione',
            },
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('progressivo', models.IntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(db_index=True, default=ufficio_soci.models.Quota.default_anno)),
                ('data_versamento', models.DateField(help_text="La data di versamento dell'importo.")),
                ('data_annullamento', models.DateField(blank=True, null=True)),
                ('stato', models.CharField(db_index=True, default='R', choices=[('R', 'Registrata'), ('X', 'Annullata')], max_length=1)),
                ('importo', models.FloatField()),
                ('importo_extra', models.FloatField(default=0.0)),
                ('causale', models.CharField(max_length=512)),
                ('causale_extra', models.CharField(max_length=512, blank=True)),
                ('annullato_da', models.ForeignKey(to='anagrafica.Persona', related_name='quote_annullate', null=True, blank=True)),
                ('appartenenza', models.ForeignKey(to='anagrafica.Appartenenza', null=True, related_name='quote')),
                ('persona', models.ForeignKey(related_name='quote', to='anagrafica.Persona')),
                ('registrato_da', models.ForeignKey(related_name='quote_registrate', to='anagrafica.Persona')),
                ('sede', models.ForeignKey(related_name='quote', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Quote',
            },
        ),
        migrations.CreateModel(
            name='Tesseramento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(default='A', choices=[('A', 'Aperto'), ('C', 'Chiuso')], max_length=1)),
                ('anno', models.SmallIntegerField(unique=True, db_index=True, default=ufficio_soci.models.Tesseramento.default_anno)),
                ('inizio', models.DateField(db_index=True, default=ufficio_soci.models.Tesseramento.default_inizio)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
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
