# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0008_auto_20160129_0103'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='area',
            index_together=set([('sede', 'obiettivo')]),
        ),
    ]
