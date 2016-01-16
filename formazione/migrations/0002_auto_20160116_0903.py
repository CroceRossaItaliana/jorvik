# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partecipazionecorsobase',
            name='stato',
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='ammissione',
            field=models.CharField(blank=True, choices=[('AM', 'Ammesso'), ('NA', 'Non Ammesso'), ('AS', 'Assente')], db_index=True, default=None, null=True, max_length=2),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='argomento_parte_1',
            field=models.TextField(blank=True, help_text='es. Storia della CRI, DIU', null=True, max_length=1024),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='argomento_parte_2',
            field=models.TextField(blank=True, help_text='es. BLS, colpo di calore', null=True, max_length=1024),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='confermata',
            field=models.BooleanField(default=True, verbose_name='Confermata', db_index=True),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='esito',
            field=models.CharField(default=None, db_index=True, null=True, max_length=2, choices=[('OK', 'Idoneo'), ('NO', 'Non Idoneo')]),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='esito_parte_1',
            field=models.CharField(choices=[('P', 'Positivo'), ('N', 'Negativo')], db_index=True, default=None, null=True, help_text='La Croce Rossa', max_length=1),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='esito_parte_2',
            field=models.CharField(choices=[('P', 'Positivo'), ('N', 'Negativo')], db_index=True, default=None, null=True, help_text='Gesti e manovre salvavita', max_length=1),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='extra_1',
            field=models.BooleanField(default=False, help_text='Prova pratica su Parte 2 sostituita da colloquio.'),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='extra_2',
            field=models.BooleanField(default=False, help_text='Verifica effettuata solo sulla Parte 1 del programma del corso.'),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='motivo_non_ammissione',
            field=models.CharField(blank=True, null=True, max_length=1025),
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='ritirata',
            field=models.BooleanField(default=False, verbose_name='Ritirata', db_index=True),
        ),
    ]
