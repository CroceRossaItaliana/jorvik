# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20160131_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locazione',
            name='geo',
            field=django.contrib.gis.db.models.fields.PointField(db_index=True, srid=4326, blank=True, geography=True, default='POINT(0.0 0.0)'),
        ),
    ]
