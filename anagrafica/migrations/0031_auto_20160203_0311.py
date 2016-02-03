# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0030_auto_20160129_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appartenenza',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
        migrations.AlterField(
            model_name='delega',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
        migrations.AlterField(
            model_name='persona',
            name='genere',
            field=models.CharField(verbose_name='Sesso', db_index=True, max_length=1, choices=[('M', 'Maschio'), ('F', 'Femmina')]),
        ),
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
        migrations.AlterField(
            model_name='riserva',
            name='fine',
            field=models.DateTimeField(verbose_name='Fine', null=True, db_index=True, default=None, blank=True),
        ),
    ]
