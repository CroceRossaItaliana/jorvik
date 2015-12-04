# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allegato',
            name='oggetto_id',
            field=models.PositiveIntegerField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='allegato',
            name='oggetto_tipo',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='allegato_come_oggetto', blank=True, null=True),
        ),
    ]
