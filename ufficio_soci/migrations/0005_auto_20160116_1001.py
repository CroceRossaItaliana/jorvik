# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0010_auto_20160115_2155'),
        ('ufficio_soci', '0004_tesseramento_quota_sostenitore'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tesserino',
            name='confermata',
        ),
        migrations.RemoveField(
            model_name='tesserino',
            name='ritirata',
        ),
        migrations.AddField(
            model_name='tesserino',
            name='codice',
            field=base.utils.UpperCaseCharField(null=True, default=None, db_index=True, max_length=13, unique=True),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='confermato_da',
            field=models.ForeignKey(null=True, to='anagrafica.Persona', related_name='tesserini_confermati'),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='data_conferma',
            field=models.DateTimeField(null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='data_riconsegna',
            field=models.DateTimeField(null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='emesso_da',
            field=models.ForeignKey(default=1, to='anagrafica.Sede', related_name='tesserini_emessi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tesserino',
            name='motivo_richiesta',
            field=models.CharField(null=True, blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='motivo_rifiutato',
            field=models.CharField(null=True, blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='richiesto_da',
            field=models.ForeignKey(default=1, to='anagrafica.Persona', related_name='tesserini_stampati_richiesti'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tesserino',
            name='riconsegnato_a',
            field=models.ForeignKey(null=True, to='anagrafica.Persona', related_name='tesserini_riconsegnati'),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='stato_emissione',
            field=models.CharField(null=True, default=None, choices=[('STAMPAT', 'Stampato'), ('SP_CASA', 'Spedito a casa'), ('SP_SEDE', 'Spedito alla Sede CRI')], max_length=8, blank=True),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='stato_richiesta',
            field=models.CharField(default='ATT', choices=[('RIF', 'Emissione Rifiutata'), ('ATT', 'Emissione Richiesta'), ('OK', 'Emissione Accettata')], db_index=True, max_length=3),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='tipo_richiesta',
            field=models.CharField(default='RIL', choices=[('RIL', 'Rilascio'), ('RIN', 'Rinnovo'), ('DUP', 'Duplicato')], db_index=True, max_length=3),
        ),
        migrations.AddField(
            model_name='tesserino',
            name='valido',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
