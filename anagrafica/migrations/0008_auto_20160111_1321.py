# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0007_auto_20160111_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estensione',
            name='motivo',
            field=models.CharField(max_length=4096, null=True),
        ),
    ]
