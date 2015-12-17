# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0002_auto_20151217_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attivita',
            name='descrizione',
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
