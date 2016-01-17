# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0003_appartenenza_vecchia_sede'),
    ]

    operations = [
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='sede',
            field=models.ForeignKey(default=1, to='anagrafica.Sede', related_name='provvedimenti'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dimissione',
            name='motivo',
            field=models.CharField(choices=[('VOL', 'Dimissioni Volontarie'), ('TUR', 'Mancato svolgimento turno'), ('RIS', 'Mancato rientro da riserva'), ('QUO', 'Mancato versamento quota annuale'), ('RAD', 'Radiazione da Croce Rossa Italiana'), ('DEC', 'Decesso')], max_length=3),
        ),
    ]
