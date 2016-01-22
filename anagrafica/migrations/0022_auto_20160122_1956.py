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
            field=models.CharField(db_index=True, choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente')], max_length=2, default='VO', verbose_name='Tipo membro'),
        ),
    ]
