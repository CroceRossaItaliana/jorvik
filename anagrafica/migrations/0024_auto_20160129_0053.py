# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0023_auto_20160128_0920'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='appartenenza',
            index_together=set([('inizio', 'fine'), ('persona', 'inizio', 'fine'), ('sede', 'inizio', 'fine'), ('sede', 'membro'), ('persona', 'sede'), ('sede', 'membro', 'inizio', 'fine')]),
        ),
        migrations.AlterIndexTogether(
            name='delega',
            index_together=set([('tipo', 'oggetto_tipo', 'oggetto_id'), ('inizio', 'fine'), ('persona', 'tipo'), ('oggetto_tipo', 'oggetto_id')]),
        ),
        migrations.AlterIndexTogether(
            name='persona',
            index_together=set([('nome', 'cognome'), ('nome', 'cognome', 'codice_fiscale')]),
        ),
        migrations.AlterIndexTogether(
            name='riserva',
            index_together=set([('inizio', 'fine'), ('persona', 'inizio', 'fine')]),
        ),
        migrations.AlterIndexTogether(
            name='sede',
            index_together=set([('attiva', 'estensione'), ('estensione', 'tipo'), ('attiva', 'tipo')]),
        ),
    ]
