# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0006_auto_20160214_0229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quota',
            name='tipo',
            field=models.CharField(default='Q', choices=[('Q', 'Quota Socio'), ('S', 'Ricevuta Sostenitore'), ('R', 'Ricevuta')], max_length=1),
        ),
    ]
