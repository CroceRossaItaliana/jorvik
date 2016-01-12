# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_log'),
        ('veicoli', '0002_auto_20160112_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='autoparco',
            name='locazione',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='veicoli_autoparco', to='base.Locazione'),
        ),
    ]
