# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='corsobase',
            name='vecchio_id',
            field=models.IntegerField(blank=True, null=True, default=None, db_index=True),
        ),
    ]
