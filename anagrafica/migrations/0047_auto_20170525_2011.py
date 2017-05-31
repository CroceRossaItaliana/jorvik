# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-05-25 20:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0046_delega_stato'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='delega',
            index_together=set([('persona', 'tipo', 'stato'), ('inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'), ('tipo', 'oggetto_tipo', 'oggetto_id'), ('persona', 'inizio', 'fine', 'tipo'), ('persona', 'inizio', 'fine', 'tipo', 'stato'), ('persona', 'stato'), ('persona', 'inizio', 'fine'), ('inizio', 'fine', 'tipo'), ('persona', 'inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'), ('persona', 'tipo'), ('oggetto_tipo', 'oggetto_id'), ('inizio', 'fine', 'stato'), ('inizio', 'fine')]),
        ),
    ]
