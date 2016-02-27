# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0008_auto_20160218_0113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tesserino',
            name='stato_emissione',
            field=models.CharField(choices=[('', '(Non emesso)'), ('STAMPAT', 'Stampato'), ('SP_CASA', 'Spedito a casa'), ('SP_SEDE', 'Spedito alla Sede CRI')], blank=True, null=True, max_length=8, default=None),
        ),
        migrations.AlterField(
            model_name='tesserino',
            name='stato_richiesta',
            field=models.CharField(choices=[('ATT', 'Emissione Richiesta'), ('RIF', 'Emissione Rifiutata'), ('OK', 'Emissione Accettata')], db_index=True, max_length=3, default='ATT'),
        ),
    ]
