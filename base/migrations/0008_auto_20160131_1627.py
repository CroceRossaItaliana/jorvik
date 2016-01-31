# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20160129_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locazione',
            name='geo',
            field=django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', srid=4326, geography=True, blank=True),
        ),
    ]
