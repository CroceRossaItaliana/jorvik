# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0009_auto_20160131_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aspirante',
            name='raggio',
            field=models.FloatField(db_index=True, default=0.0, blank=True, verbose_name='Raggio KM', null=True),
        ),
    ]
