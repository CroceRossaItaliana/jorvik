# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gruppi', '0003_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appartenenza',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
    ]
