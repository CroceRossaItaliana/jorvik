# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autorizzazione',
            name='motivo_negazione',
            field=models.CharField(null=True, blank=True, max_length=512),
        ),
    ]
