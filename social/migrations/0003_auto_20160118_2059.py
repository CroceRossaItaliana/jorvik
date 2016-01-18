# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commento',
            name='oggetto_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='giudizio',
            name='oggetto_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='contenttypes.ContentType'),
        ),
    ]
