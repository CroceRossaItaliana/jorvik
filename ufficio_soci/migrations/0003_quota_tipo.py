# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0002_tesserino_persona'),
    ]

    operations = [
        migrations.AddField(
            model_name='quota',
            name='tipo',
            field=models.CharField(choices=[('Q', 'Quota Socio'), ('S', 'Quota Sostenitore'), ('R', 'Ricevuta')], default='Q', max_length=1),
        ),
    ]
