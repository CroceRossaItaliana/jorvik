# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0006_auto_20160124_1740'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='corsobase',
            options={'verbose_name': 'Corso Base', 'verbose_name_plural': 'Corsi Base', 'ordering': ['-data_inizio']},
        ),
    ]
