# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0026_auto_20160129_0103'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='sede',
            index_together=set([('lft', 'rght', 'attiva', 'estensione'), ('lft', 'rght', 'attiva'), ('attiva', 'tipo'), ('genitore', 'estensione'), ('lft', 'rght', 'tree_id'), ('estensione', 'tipo'), ('attiva', 'estensione'), ('lft', 'rght')]),
        ),
    ]
