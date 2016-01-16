# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gruppi', '0002_auto_20160116_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gruppo',
            name='attivita',
            field=models.ForeignKey(related_name='gruppi', to='attivita.Attivita', null=True),
        ),
    ]
