# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_ean13'),
    ]

    operations = [
        migrations.AddField(
            model_name='allegato',
            name='scadenza',
            field=models.DateTimeField(db_index=True, verbose_name='Scadenza', blank=True, null=True, default=None),
        ),
    ]
