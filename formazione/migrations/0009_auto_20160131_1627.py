# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0008_auto_20160129_0044'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='corsobase',
            options={'verbose_name_plural': 'Corsi Base', 'ordering': ['-anno', '-progressivo'], 'verbose_name': 'Corso Base'},
        ),
    ]
