# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0004_auto_20160117_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assenzacorsobase',
            name='registrata_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='assenze_corsi_base_registrate', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='lezionecorsobase',
            name='corso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lezioni', to='formazione.CorsoBase'),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='corso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='partecipazioni', to='formazione.CorsoBase'),
        ),
    ]
