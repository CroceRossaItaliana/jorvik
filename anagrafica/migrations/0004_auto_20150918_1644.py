# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0003_remove_persona_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='delega',
            name='firmatario',
            field=models.ForeignKey(related_query_name='delega_firmata', null=True, default=None, to='anagrafica.Persona', related_name='deleghe_firmate'),
        ),
        migrations.AlterField(
            model_name='appartenenza',
            name='terminazione',
            field=models.CharField(blank=True, null=True, max_length=1, db_index=True, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione')], default=None, verbose_name='Terminazione'),
        ),
        migrations.AlterField(
            model_name='delega',
            name='persona',
            field=models.ForeignKey(related_query_name='delega', to='anagrafica.Persona', related_name='deleghe'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='email_contatto',
            field=models.EmailField(blank=True, max_length=64, verbose_name='Email di contatto'),
        ),
    ]
