# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import anagrafica.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0006_auto_20160110_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='data_nascita',
            field=models.DateField(verbose_name='Data di nascita', validators=[anagrafica.validators.valida_almeno_14_anni], null=True, db_index=True),
        ),
    ]
