# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2018-04-08 19:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0017_chiudi_attivita_vecchie'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partecipazione',
            options={'ordering': ('stato', 'persona__cognome', 'persona__nome'), 'permissions': (('view_partecipazione', 'Can view partecipazione'),), 'verbose_name': 'Richiesta di partecipazione', 'verbose_name_plural': 'Richieste di partecipazione'},
        ),
    ]
