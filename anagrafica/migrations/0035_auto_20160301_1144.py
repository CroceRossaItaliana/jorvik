# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0034_sede_sito_web'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='appartenenza',
            index_together=set([('membro', 'confermata', 'sede'), ('sede', 'inizio', 'fine'), ('membro', 'confermata', 'persona'), ('confermata', 'persona'), ('persona', 'inizio', 'fine', 'membro'), ('sede', 'membro'), ('inizio', 'fine'), ('persona', 'inizio', 'fine'), ('persona', 'inizio', 'fine', 'membro', 'confermata'), ('id', 'sede', 'membro', 'inizio', 'fine'), ('sede', 'membro', 'inizio', 'fine'), ('persona', 'sede'), ('membro', 'confermata'), ('membro', 'confermata', 'inizio', 'fine')]),
        ),
    ]
