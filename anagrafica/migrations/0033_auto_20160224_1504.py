# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import anagrafica.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0032_auto_20160224_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='iban',
            field=models.CharField(validators=[anagrafica.validators.valida_iban], help_text='Coordinate bancarie internazionali del C/C della Sede.', verbose_name='IBAN', max_length=32, blank=True),
        ),
        migrations.AlterField(
            model_name='sede',
            name='partita_iva',
            field=models.CharField(validators=[anagrafica.validators.valida_partita_iva], max_length=32, verbose_name='Partita IVA', blank=True),
        ),
    ]
