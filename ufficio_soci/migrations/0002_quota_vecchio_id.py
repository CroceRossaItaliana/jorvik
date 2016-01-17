# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quota',
            name='vecchio_id',
            field=models.IntegerField(null=True, default=None, blank=True, db_index=True),
        ),
    ]
