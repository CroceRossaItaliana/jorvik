# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0028_auto_20160129_0115'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='appartenenza',
            index_together=set([('persona', 'inizio', 'fine'), ('sede', 'membro'), ('membro', 'confermata'), ('sede', 'membro', 'inizio', 'fine'), ('inizio', 'fine'), ('sede', 'inizio', 'fine'), ('membro', 'confermata', 'inizio', 'fine'), ('membro', 'confermata', 'persona'), ('persona', 'inizio', 'fine', 'membro', 'confermata'), ('persona', 'inizio', 'fine', 'membro'), ('persona', 'sede'), ('confermata', 'persona')]),
        ),
        migrations.AlterIndexTogether(
            name='delega',
            index_together=set([('persona', 'inizio', 'fine'), ('inizio', 'fine', 'tipo'), ('persona', 'tipo'), ('inizio', 'fine'), ('tipo', 'oggetto_tipo', 'oggetto_id'), ('oggetto_tipo', 'oggetto_id'), ('persona', 'inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'), ('inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'), ('persona', 'inizio', 'fine', 'tipo')]),
        ),
    ]
