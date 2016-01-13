# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
        ('ufficio_soci', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tesserino',
            name='persona',
            field=models.ForeignKey(related_name='tesserini', default=1, to='anagrafica.Persona'),
            preserve_default=False,
        ),
    ]
