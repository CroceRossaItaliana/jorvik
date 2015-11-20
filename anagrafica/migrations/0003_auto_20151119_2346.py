# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151119_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='indirizzo_residenza',
            field=models.CharField(max_length=512, blank=True, verbose_name='Indirizzo di residenza'),
        ),
    ]
