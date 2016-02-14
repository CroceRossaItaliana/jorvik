# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0005_auto_20160210_1900'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quota',
            options={'verbose_name_plural': 'Quote', 'ordering': ['anno', 'progressivo']},
        ),
    ]
