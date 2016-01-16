# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import gruppi.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0011_auto_20160116_1052'),
        ('attivita', '0002_auto_20160110_1425'),
        ('gruppi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appartenenza',
            name='confermata',
        ),
        migrations.RemoveField(
            model_name='appartenenza',
            name='ritirata',
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='fine',
            field=models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', default=None, db_index=True, blank=True, null=True, verbose_name='Fine'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='gruppo',
            field=models.ForeignKey(to='gruppi.Gruppo', default=1, related_name='appartenenze'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='inizio',
            field=models.DateTimeField(verbose_name='Inizio', db_index=True, default=datetime.datetime(2016, 1, 16, 10, 53, 4, 101360)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='motivo_negazione',
            field=models.CharField(max_length=512, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='negato_da',
            field=models.ForeignKey(to='anagrafica.Persona', null=True, related_name='appartenenze_gruppi_negate'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', default=1, related_name='appartenenze_gruppi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gruppo',
            name='area',
            field=models.ForeignKey(to='attivita.Area', default=1, related_name='gruppi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gruppo',
            name='attivita',
            field=models.ForeignKey(to='attivita.Attivita', default=1, related_name='gruppi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gruppo',
            name='obiettivo',
            field=models.IntegerField(default=1, db_index=True, validators=[gruppi.models.tra_1_e_6]),
            preserve_default=False,
        ),
    ]
