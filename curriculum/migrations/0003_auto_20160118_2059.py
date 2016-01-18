# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titolopersonale',
            name='certificato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='titoli_da_me_certificati', null=True, to='anagrafica.Persona'),
        ),
    ]
