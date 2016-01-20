# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autorizzazione',
            name='destinatario_ruolo',
            field=models.CharField(db_index=True, max_length=16, choices=[('PRES', 'Presidenza'), ('US-GEN', 'Gestione dei Soci'), ('US-TRASF', 'Gestione dei Trasferimenti'), ('US-EST', 'Gestione delle Estensioni'), ('US-FOT', 'Gestione delle Fototessere'), ('US-TIT', 'Gestione dei Titoli nella Sede'), ('US-RIS', 'Gestione delle Riserve'), ('ATT-PART', "Gestione dei Partecipanti all'Attività"), ('CB-PART', 'Gestione dei Partecipanti al Corso Base'), ('US-APP', 'Gestione degli Appartenenti alla Sede'), ('SA-SAN', 'Gestione delle Donazioni Sangue')]),
        ),
    ]
