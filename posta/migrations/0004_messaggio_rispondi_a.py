# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0031_auto_20160203_0311'),
        ('posta', '0003_auto_20160207_0618'),
    ]

    operations = [
        migrations.AddField(
            model_name='messaggio',
            name='rispondi_a',
            field=models.ForeignKey(related_name='messaggi_come_rispondi_a', blank=True, null=True, to='anagrafica.Persona', default=None),
        ),
    ]
