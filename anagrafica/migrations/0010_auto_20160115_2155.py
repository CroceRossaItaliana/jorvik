# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import anagrafica.validators
import base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
    ]

    operations = [


        migrations.AlterField(
            model_name='persona',
            name='codice_fiscale',
            field=base.utils.UpperCaseCharField(db_index=True, validators=[anagrafica.validators.valida_codice_fiscale], verbose_name='Codice Fiscale', unique=True, max_length=16),
        ),
    ]
