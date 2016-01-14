# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0003_quota_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='tesseramento',
            name='quota_sostenitore',
            field=models.FloatField(default=20.0),
        ),
    ]
