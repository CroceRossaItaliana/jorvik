# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0008_auto_20160117_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='persona',
            name='cm',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='persona',
            name='conoscenza',
            field=models.CharField(db_index=True, max_length=2, null=True, default=None, blank=True),
        ),
        migrations.AddField(
            model_name='persona',
            name='iv',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='riserva',
            name='appartenenza',
            field=models.ForeignKey(to='anagrafica.Appartenenza', related_name='riserve'),
        ),
        migrations.AlterField(
            model_name='riserva',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='riserve'),
        ),
    ]
