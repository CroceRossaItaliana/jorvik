# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0002_auto_20160116_0903'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partecipazionecorsobase',
            old_name='esito',
            new_name='esito_esame',
        ),
    ]
