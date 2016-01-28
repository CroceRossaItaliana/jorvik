# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0007_auto_20160128_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='esito_esame',
            field=models.CharField(choices=[('OK', 'Idoneo'), ('NO', 'Non Idoneo')], blank=True, default=None, max_length=2, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='esito_parte_1',
            field=models.CharField(choices=[('P', 'Positivo'), ('N', 'Negativo')], blank=True, default=None, max_length=1, null=True, db_index=True, help_text='La Croce Rossa'),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='esito_parte_2',
            field=models.CharField(choices=[('P', 'Positivo'), ('N', 'Negativo')], blank=True, default=None, max_length=1, null=True, db_index=True, help_text='Gesti e manovre salvavita'),
        ),
    ]
