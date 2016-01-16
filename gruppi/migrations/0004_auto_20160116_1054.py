# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gruppi', '0003_auto_20160116_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gruppo',
            name='nome',
            field=models.CharField(max_length=255, verbose_name='Nome'),
        ),
    ]
