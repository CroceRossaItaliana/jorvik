# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0011_remove_attivita_centrale_operativa'),
    ]

    operations = [
        migrations.AddField(
            model_name='attivita',
            name='centrale_operativa',
            field=models.CharField(null=True, max_length=1, default=None, blank=True, help_text="Selezionando questa opzione, i partecipanti confermati verranno abilitati, automaticamente o manualmente dal delegato CO, all'uso del pannello di Centrale Operativa della Sede da 15 minuti prima dell'inizio a 15 minuti dopo la fine del turno.", choices=[(None, '(Disattiva)'), ('A', 'Automatica'), ('M', 'Manuale')], db_index=True, verbose_name='Attività di Centrale Operativa'),
        ),
    ]
