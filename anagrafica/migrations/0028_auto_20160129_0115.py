# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0027_auto_20160129_0109'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='appartenenza',
            index_together=set([('sede', 'inizio', 'fine'), ('persona', 'inizio', 'fine'), ('inizio', 'fine'), ('membro', 'confermata', 'persona'), ('confermata', 'persona'), ('membro', 'confermata', 'inizio', 'fine'), ('sede', 'membro', 'inizio', 'fine'), ('persona', 'sede'), ('sede', 'membro'), ('membro', 'confermata')]),
        ),
    ]
