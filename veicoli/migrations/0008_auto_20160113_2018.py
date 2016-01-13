# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0007_auto_20160113_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veicolo',
            name='carrozzeria',
            field=models.CharField(help_text='es. Chiuso', max_length=128, verbose_name='Carrozzeria (J.2)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='categoria',
            field=models.CharField(help_text='es. Ambulanza', max_length=128, db_index=True, verbose_name='Categoria del Veicolo (J)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='destinazione',
            field=models.CharField(help_text='es. Amb. Soccorso (AMB-A)', max_length=128, verbose_name='Destinazione ed uso (J.1)'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='pneumatici_alt_anteriori',
            field=models.CharField(help_text='es. 215/70 R12C', max_length=255, blank=True, null=True, verbose_name='Pneumatici alternativi: Anteriori'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='pneumatici_alt_posteriori',
            field=models.CharField(help_text='es. 215/70 R12C', max_length=255, blank=True, null=True, verbose_name='Pneumatici alternativi: Posteriori'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='pneumatici_anteriori',
            field=models.CharField(help_text='es. 215/70 R12C', max_length=255, verbose_name='Pneumatici: Anteriori'),
        ),
        migrations.AlterField(
            model_name='veicolo',
            name='pneumatici_posteriori',
            field=models.CharField(help_text='es. 215/70 R12C', max_length=255, verbose_name='Pneumatici: Posteriori'),
        ),
    ]
