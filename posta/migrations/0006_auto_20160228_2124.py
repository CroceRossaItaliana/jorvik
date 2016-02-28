# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posta', '0005_auto_20160219_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messaggio',
            name='oggetto',
            field=models.CharField(default='(Nessun oggetto)', max_length=256, db_index=True),
        ),
    ]
