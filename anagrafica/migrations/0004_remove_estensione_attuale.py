# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0003_auto_20160110_1836'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estensione',
            name='attuale',
        ),
    ]
