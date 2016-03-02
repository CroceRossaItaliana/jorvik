# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0036_auto_20160301_1209'),
        ('formazione', '0011_auto_20160203_0311'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partecipazionecorsobase',
            options={'ordering': ('persona__nome', 'persona__cognome', 'persona__codice_fiscale'), 'verbose_name': 'Richiesta di partecipazione', 'verbose_name_plural': 'Richieste di partecipazione'},
        ),
        migrations.AddField(
            model_name='partecipazionecorsobase',
            name='destinazione',
            field=models.ForeignKey(null=True, verbose_name='Sede di destinazione', to='anagrafica.Sede', default=None, related_name='aspiranti_destinati', help_text="La Sede presso la quale verrà registrato come Volontario l'aspirante nel caso di superamento dell'esame.", blank=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='argomento_parte_1',
            field=models.CharField(help_text='es. Storia della CRI, DIU', null=True, max_length=1024, blank=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='argomento_parte_2',
            field=models.CharField(help_text='es. BLS, colpo di calore', null=True, max_length=1024, blank=True),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='extra_1',
            field=models.BooleanField(verbose_name='Prova pratica su Parte 2 sostituita da colloquio.', default=False),
        ),
        migrations.AlterField(
            model_name='partecipazionecorsobase',
            name='extra_2',
            field=models.BooleanField(verbose_name='Verifica effettuata solo sulla Parte 1 del programma del corso.', default=False),
        ),
    ]
