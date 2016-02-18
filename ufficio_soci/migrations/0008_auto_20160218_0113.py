# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0007_auto_20160218_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tesserino',
            name='stato_emissione',
            field=models.CharField(blank=True, null=True, default=None, choices=[(None, '(Non emesso)'), ('STAMPAT', 'Stampato'), ('SP_CASA', 'Spedito a casa'), ('SP_SEDE', 'Spedito alla Sede CRI')], max_length=8),
        ),
    ]
