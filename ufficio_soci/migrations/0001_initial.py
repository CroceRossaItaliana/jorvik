# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ufficio_soci.models
import base.utils
import base.tratti


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('progressivo', models.IntegerField(db_index=True)),
                ('anno', models.SmallIntegerField(db_index=True)),
                ('data_versamento', models.DateField(help_text="La data di versamento dell'importo.")),
                ('data_annullamento', models.DateField(blank=True, null=True)),
                ('stato', models.CharField(max_length=1, db_index=True, default='R', choices=[('R', 'Registrata'), ('X', 'Annullata')])),
                ('tipo', models.CharField(max_length=1, default='Q', choices=[('Q', 'Quota Socio'), ('S', 'Quota Sostenitore'), ('R', 'Ricevuta')])),
                ('importo', models.FloatField()),
                ('importo_extra', models.FloatField(default=0.0)),
                ('causale', models.CharField(max_length=512)),
                ('causale_extra', models.CharField(blank=True, max_length=512)),
                ('annullato_da', models.ForeignKey(related_name='quote_annullate', blank=True, to='anagrafica.Persona', null=True)),
                ('appartenenza', models.ForeignKey(related_name='quote', to='anagrafica.Appartenenza', null=True)),
                ('persona', models.ForeignKey(related_name='quote', to='anagrafica.Persona')),
                ('registrato_da', models.ForeignKey(related_name='quote_registrate', to='anagrafica.Persona')),
                ('sede', models.ForeignKey(related_name='quote', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Quote',
            },
            bases=(models.Model, base.tratti.ConPDF),
        ),
        migrations.CreateModel(
            name='Tesseramento',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(max_length=1, default='A', choices=[('A', 'Aperto'), ('C', 'Chiuso')])),
                ('anno', models.SmallIntegerField(unique=True, db_index=True)),
                ('inizio', models.DateField(db_index=True)),
                ('quota_attivo', models.FloatField(default=8.0)),
                ('quota_ordinario', models.FloatField(default=16.0)),
                ('quota_benemerito', models.FloatField(default=20.0)),
                ('quota_aspirante', models.FloatField(default=20.0)),
                ('quota_sostenitore', models.FloatField(default=20.0)),
            ],
            options={
                'verbose_name_plural': 'Tesseramenti',
                'verbose_name': 'Tesseramento',
            },
        ),
        migrations.CreateModel(
            name='Tesserino',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo_richiesta', models.CharField(max_length=3, db_index=True, default='RIL', choices=[('RIL', 'Rilascio'), ('RIN', 'Rinnovo'), ('DUP', 'Duplicato')])),
                ('stato_richiesta', models.CharField(max_length=3, db_index=True, default='ATT', choices=[('RIF', 'Emissione Rifiutata'), ('ATT', 'Emissione Richiesta'), ('OK', 'Emissione Accettata')])),
                ('motivo_richiesta', models.CharField(blank=True, max_length=512, null=True)),
                ('motivo_rifiutato', models.CharField(blank=True, max_length=512, null=True)),
                ('stato_emissione', models.CharField(max_length=8, blank=True, default=None, choices=[('STAMPAT', 'Stampato'), ('SP_CASA', 'Spedito a casa'), ('SP_SEDE', 'Spedito alla Sede CRI')], null=True)),
                ('valido', models.BooleanField(db_index=True, default=False)),
                ('codice', base.utils.UpperCaseCharField(unique=True, db_index=True, default=None, max_length=13, null=True)),
                ('data_conferma', models.DateTimeField(db_index=True, null=True)),
                ('data_riconsegna', models.DateTimeField(db_index=True, null=True)),
                ('confermato_da', models.ForeignKey(related_name='tesserini_confermati', to='anagrafica.Persona', null=True)),
                ('emesso_da', models.ForeignKey(related_name='tesserini_emessi', to='anagrafica.Sede')),
                ('persona', models.ForeignKey(related_name='tesserini', to='anagrafica.Persona')),
                ('richiesto_da', models.ForeignKey(related_name='tesserini_stampati_richiesti', to='anagrafica.Persona')),
                ('riconsegnato_a', models.ForeignKey(related_name='tesserini_riconsegnati', to='anagrafica.Persona', null=True)),
            ],
            options={
                'verbose_name_plural': 'Richieste Tesserino Associativo',
                'verbose_name': 'Richiesta Tesserino Associativo',
            },
        ),
        migrations.AlterUniqueTogether(
            name='quota',
            unique_together=set([('progressivo', 'anno', 'sede')]),
        ),
    ]
