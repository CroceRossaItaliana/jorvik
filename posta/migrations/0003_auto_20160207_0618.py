# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posta', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destinatario',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', default=None, null=True, blank=True, related_name='oggetti_sono_destinatario'),
        ),
    ]
