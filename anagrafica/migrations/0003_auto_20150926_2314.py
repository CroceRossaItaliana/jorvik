# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20150924_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='data_nascita',
            field=models.DateField(verbose_name='Data di nascita', db_index=True, null=True),
        ),
    ]
