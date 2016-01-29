# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0029_auto_20160129_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='cm',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Corpo Militare'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='iv',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Infermiera V.'),
        ),
    ]
