# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20160131_1645'),
    ]

    operations = [
        migrations.CreateModel(
            name='EAN13',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('base.allegato',),
        ),
    ]
