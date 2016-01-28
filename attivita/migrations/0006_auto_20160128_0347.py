# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import attivita.models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0005_auto_20160122_1956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='area',
            options={'verbose_name_plural': 'Aree', 'ordering': ['sede', 'obiettivo', 'nome']},
        ),
        migrations.AlterModelOptions(
            name='attivita',
            options={'verbose_name': 'Attività', 'verbose_name_plural': 'Attività', 'ordering': ['-creazione', 'nome']},
        ),
        migrations.AlterField(
            model_name='area',
            name='obiettivo',
            field=models.SmallIntegerField(db_index=True, validators=[attivita.models.valida_numero_obiettivo], default=1),
        ),
        migrations.AlterField(
            model_name='attivita',
            name='nome',
            field=models.CharField(max_length=255, db_index=True, help_text='es. Aggiungi un posto a tavola', default='Nuova attività'),
        ),
    ]
