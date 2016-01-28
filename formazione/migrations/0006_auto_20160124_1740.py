# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0005_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lezionecorsobase',
            options={'verbose_name': 'Lezione di Corso Base', 'ordering': ['inizio'], 'verbose_name_plural': 'Lezioni di Corsi Base'},
        ),
    ]
