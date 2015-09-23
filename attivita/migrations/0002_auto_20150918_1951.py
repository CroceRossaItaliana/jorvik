# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='partecipazione',
            name='ritirata',
            field=models.BooleanField(verbose_name='Ritirata', db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='partecipazione',
            name='stato',
            field=models.CharField(choices=[('K', 'Richiesta'), ('X', 'Ritirata'), ('N', 'Non presentato')], max_length=1, db_index=True, default='K'),
        ),
    ]
