# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0008_auto_20160111_1321'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estensione',
            options={'verbose_name_plural': 'Richieste di estensione', 'verbose_name': 'Richiesta di estensione'},
        ),
        migrations.AlterModelOptions(
            name='trasferimento',
            options={'verbose_name_plural': 'Richieste di trasferimento', 'verbose_name': 'Richiesta di trasferimento'},
        ),
    ]
