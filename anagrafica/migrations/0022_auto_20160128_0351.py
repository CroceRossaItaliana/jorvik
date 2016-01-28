# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0021_termina_deleghe_sedi_disattive'),
    ]

    operations = [

        migrations.AlterField(
            model_name='appartenenza',
            name='membro',
            field=models.CharField(choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente')], verbose_name='Tipo membro', max_length=2, default='VO', db_index=True),
        ),
        migrations.AlterField(
            model_name='dimissione',
            name='appartenenza',
            field=models.ForeignKey(to='anagrafica.Appartenenza', related_name='dimissioni'),
        ),
        migrations.AlterField(
            model_name='estensione',
            name='appartenenza',
            field=models.ForeignKey(null=True, to='anagrafica.Appartenenza', related_name='estensione', blank=True),
        ),
    ]
