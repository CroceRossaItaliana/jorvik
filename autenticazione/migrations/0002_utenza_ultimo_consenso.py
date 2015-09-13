# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autenticazione', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='utenza',
            name='ultimo_consenso',
            field=models.DateTimeField(blank=True, verbose_name='Ultimo consenso', null=True),
        ),
    ]
