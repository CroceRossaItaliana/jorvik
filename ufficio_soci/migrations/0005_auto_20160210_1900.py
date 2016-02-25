# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0004_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quota',
            name='anno',
            field=models.SmallIntegerField(db_index=True, default=base.utils.questo_anno),
        ),
        migrations.AlterField(
            model_name='tesseramento',
            name='anno',
            field=models.SmallIntegerField(db_index=True, unique=True, default=base.utils.questo_anno),
        ),
        migrations.AlterField(
            model_name='tesseramento',
            name='inizio',
            field=models.DateField(db_index=True, default=base.utils.oggi),
        ),
    ]
