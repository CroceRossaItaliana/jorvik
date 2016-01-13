# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
        ('veicoli', '0013_auto_20160113_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='fermotecnico',
            name='creato_da',
            field=models.ForeignKey(default=1, to='anagrafica.Persona', related_name='fermi_tecnici_creati'),
            preserve_default=False,
        ),
    ]
