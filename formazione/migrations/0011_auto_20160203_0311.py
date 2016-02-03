# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0010_auto_20160131_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lezionecorsobase',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
    ]
