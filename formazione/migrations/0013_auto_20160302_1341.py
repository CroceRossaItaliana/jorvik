# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0012_auto_20160301_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='argomento_parte_1',
            field=models.CharField(blank=True, max_length=1024, help_text='es. Storia della CRI, DIU.', null=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='argomento_parte_2',
            field=models.CharField(blank=True, max_length=1024, help_text='es. BLS, colpo di calore.', null=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='esito_parte_1',
            field=models.CharField(max_length=1, choices=[('P', 'Positivo'), ('N', 'Negativo')], db_index=True, blank=True, help_text='La Croce Rossa.', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='esito_parte_2',
            field=models.CharField(max_length=1, choices=[('P', 'Positivo'), ('N', 'Negativo')], db_index=True, blank=True, help_text='Gesti e manovre salvavita.', default=None, null=True),
        ),
    ]
