# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20150824_1950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persona',
            name='deleted',
        ),
    ]
