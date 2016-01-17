# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20160116_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='appartenenza',
            name='vecchia_sede',
            field=models.ForeignKey(null=True, blank=True, related_name='appartenenze_vecchie', to='anagrafica.Sede'),
        ),
    ]
