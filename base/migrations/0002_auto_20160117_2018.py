# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0008_auto_20160117_2018'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='codice',
            field=models.CharField(unique=True, max_length=128, default=1, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='persona',
            field=models.ForeignKey(related_name='tokens', default=1, to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='redirect',
            field=models.CharField(max_length=128, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='token',
            name='valido_ore',
            field=models.IntegerField(default=24),
        ),
        migrations.AlterField(
            model_name='allegato',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='autorizzazione',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='locazione',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='token',
            name='creazione',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]
