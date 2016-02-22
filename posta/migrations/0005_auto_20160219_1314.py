# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posta', '0004_messaggio_rispondi_a'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destinatario',
            name='errore',
            field=models.CharField(default=None, db_index=True, null=True, blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='destinatario',
            name='inviato',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='destinatario',
            name='tentativo',
            field=models.DateTimeField(default=None, db_index=True, null=True, blank=True),
        ),
    ]
