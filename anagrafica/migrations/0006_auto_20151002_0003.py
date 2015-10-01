# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0005_auto_20150926_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='indirizzo_residenza',
            field=models.CharField(verbose_name='Indirizzo di residenza', max_length=256, blank=True),
        ),
    ]
