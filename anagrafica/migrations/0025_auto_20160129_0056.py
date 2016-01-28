# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0024_auto_20160129_0053'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='delega',
            index_together=set([('persona', 'tipo'), ('inizio', 'fine', 'tipo'), ('inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'), ('inizio', 'fine'), ('oggetto_tipo', 'oggetto_id'), ('tipo', 'oggetto_tipo', 'oggetto_id'), ('persona', 'inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'), ('persona', 'inizio', 'fine', 'tipo')]),
        ),
    ]
