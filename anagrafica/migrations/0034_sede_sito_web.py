# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0033_auto_20160224_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='sito_web',
            field=models.URLField(help_text='URL completo del sito web, es.: http://www.cri.it/.', blank=True, verbose_name='Sito Web'),
        ),
    ]
