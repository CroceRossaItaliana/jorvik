# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0003_auto_20150926_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='cap_residenza',
            field=models.CharField(blank=True, verbose_name='CAP di Residenza', max_length=16),
        ),
    ]
