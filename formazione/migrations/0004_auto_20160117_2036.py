# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0003_auto_20160117_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='corsobase',
            name='data_attivazione',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='corsobase',
            name='data_convocazione',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='corsobase',
            name='op_attivazione',
            field=models.CharField(blank=True, null=True, max_length=255),
        ),
        migrations.AddField(
            model_name='corsobase',
            name='op_convocazione',
            field=models.CharField(blank=True, null=True, max_length=255),
        ),
    ]
