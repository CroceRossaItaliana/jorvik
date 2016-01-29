# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0025_auto_20160129_0056'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='sede',
            index_together=set([('estensione', 'tipo'), ('lft', 'rght', 'tree_id'), ('attiva', 'tipo'), ('lft', 'rght'), ('attiva', 'estensione'), ('lft', 'rght', 'attiva'), ('lft', 'rght', 'attiva', 'estensione')]),
        ),
        migrations.AlterIndexTogether(
            name='telefono',
            index_together=set([('persona', 'servizio')]),
        ),
    ]
