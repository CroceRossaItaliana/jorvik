# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0009_auto_20160113_1952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sospensione',
            name='provvedimento',
        ),
        migrations.RemoveField(
            model_name='sospensione',
            name='provvedimentodisciplinare_ptr',
        ),
        migrations.DeleteModel(
            name='Sospensione',
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='fine',
            field=models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', blank=True, null=True, db_index=True, verbose_name='Fine', default=None),
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='inizio',
            field=models.DateTimeField(verbose_name='Inizio', default=datetime.datetime(2016, 1, 15, 21, 34, 19, 384739), db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='tipo',
            field=models.CharField(max_length=1, choices=[('A', 'Ammonizione'), ('S', 'Sospensione'), ('E', 'Esplusione')], default='A'),
        ),

    ]
