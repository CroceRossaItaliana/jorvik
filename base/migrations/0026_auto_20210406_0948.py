# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-04-06 09:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_autorizzazione_mail_verifica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autorizzazione',
            name='destinatario_ruolo',
            field=models.CharField(choices=[('PRES', 'Presidenza'), ('COM', 'Commissario'), ('US-GEN', 'Gestione dei Soci'), ('US-TRASF', 'Gestione dei Trasferimenti'), ('US-EST', 'Gestione delle Estensioni'), ('US-FOT', 'Gestione delle Fototessere'), ('US-TIT', 'Gestione dei Titoli nella Sede'), ('US-RIS', 'Gestione delle Riserve'), ('ATT-PART', "Gestione dei Partecipanti all'Attività"), ('SOS-PART', 'Gestione dei Partecipanti al Servizio SO'), ('CB-PART', 'Gestione dei Partecipanti al Corso Base'), ('US-APP', 'Gestione degli Appartenenti alla Sede'), ('SA-SAN', 'Gestione delle Donazioni Sangue'), ('ASP', 'Autogestione Aspirante'), ('EVN-PART', 'Responsabile Evento')], db_index=True, max_length=16),
        ),
    ]
