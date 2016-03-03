# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0010_attivita_centrale_operativa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attivita',
            name='centrale_operativa',
        ),
    ]
