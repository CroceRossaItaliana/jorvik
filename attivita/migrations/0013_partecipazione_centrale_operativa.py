# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0012_attivita_centrale_operativa'),
    ]

    operations = [
        migrations.AddField(
            model_name='partecipazione',
            name='centrale_operativa',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
