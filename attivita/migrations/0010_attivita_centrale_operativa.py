# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0009_auto_20160129_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='centrale_operativa',
            field=models.BooleanField(verbose_name='Attività di Centrale Operativa', default=False, db_index=True, help_text="Selezionando questa opzione, i partecipanti confermati verranno abilitati all'uso del pannello di Centrale Operativa della Sede da 15 minuti prima dell'inizio a 15 minuti dopo la fine del turno."),
        ),
    ]
