# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0004_auto_20160118_2059'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partecipazione',
            options={'ordering': ['stato', 'persona__nome', 'persona__cognome'], 'verbose_name_plural': 'Richieste di partecipazione', 'verbose_name': 'Richiesta di partecipazione'},
        ),
        migrations.AlterModelOptions(
            name='turno',
            options={'ordering': ['inizio', 'fine', 'id'], 'verbose_name_plural': 'Turni'},
        ),
        migrations.AlterField(
            model_name='partecipazione',
            name='stato',
            field=models.CharField(db_index=True, choices=[('K', 'Part. Richiesta'), ('N', 'Non presentato/a')], default='K', max_length=1),
        ),
        migrations.AlterField(
            model_name='turno',
            name='fine',
            field=models.DateTimeField(db_index=True, blank=True, null=True, default=None, verbose_name='Data e ora di fine'),
        ),
        migrations.AlterField(
            model_name='turno',
            name='inizio',
            field=models.DateTimeField(db_index=True, verbose_name='Data e ora di inizio'),
        ),
        migrations.AlterField(
            model_name='turno',
            name='massimo',
            field=models.SmallIntegerField(db_index=True, blank=True, null=True, default=None, verbose_name='Num. massimo di partecipanti'),
        ),
        migrations.AlterField(
            model_name='turno',
            name='minimo',
            field=models.SmallIntegerField(db_index=True, default=1, verbose_name='Num. minimo di partecipanti'),
        ),
    ]
