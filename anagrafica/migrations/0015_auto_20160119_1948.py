# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0014_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='email_contatto',
            field=models.EmailField(blank=True, max_length=255, verbose_name='Email di contatto'),
        ),
    ]
