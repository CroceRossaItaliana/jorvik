# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0035_auto_20160301_1144'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='persona',
            index_together=set([('nome', 'cognome', 'codice_fiscale'), ('nome', 'cognome'), ('id', 'nome', 'cognome', 'codice_fiscale')]),
        ),
    ]
