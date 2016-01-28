# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0006_auto_20160128_0347'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='partecipazione',
            index_together=set([('persona', 'turno', 'stato'), ('turno', 'stato'), ('persona', 'turno')]),
        ),
        migrations.AlterIndexTogether(
            name='turno',
            index_together=set([('inizio', 'fine'), ('attivita', 'inizio'), ('attivita', 'inizio', 'fine')]),
        ),
    ]
