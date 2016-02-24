# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0031_auto_20160203_0311'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='pec',
            field=models.EmailField(verbose_name='Indirizzo PEC', max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='sede',
            name='email',
            field=models.EmailField(verbose_name='Indirizzo e-mail', max_length=64, blank=True),
        ),
    ]
