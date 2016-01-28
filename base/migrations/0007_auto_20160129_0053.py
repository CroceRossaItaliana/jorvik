# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_aut_corsi_vecchi_2'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='autorizzazione',
            index_together=set([('destinatario_oggetto_tipo', 'destinatario_oggetto_id'), ('necessaria', 'destinatario_ruolo', 'destinatario_oggetto_tipo', 'destinatario_oggetto_id'), ('destinatario_ruolo', 'destinatario_oggetto_tipo', 'destinatario_oggetto_id'), ('destinatario_ruolo', 'destinatario_oggetto_tipo'), ('necessaria', 'progressivo'), ('necessaria', 'destinatario_oggetto_tipo', 'destinatario_oggetto_id'), ('necessaria', 'concessa')]),
        ),
    ]
