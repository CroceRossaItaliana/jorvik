# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0013_auto_20160118_1317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='riserva',
            options={'verbose_name_plural': 'Richieste di riserva', 'verbose_name': 'Richiesta di riserva'},
        ),
        migrations.AlterField(
            model_name='appartenenza',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appartenenze', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='appartenenza',
            name='vecchia_sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='appartenenze_vecchie', blank=True, null=True, to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='delega',
            name='firmatario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, related_name='deleghe_firmate', null=True, related_query_name='delega_firmata', to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='delega',
            name='oggetto_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='dimissione',
            name='appartenenza',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dimissioni', to='anagrafica.Appartenenza'),
        ),
        migrations.AlterField(
            model_name='dimissione',
            name='richiedente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='dimissione',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dimissioni', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='estensione',
            name='appartenenza',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='estensione', blank=True, null=True, to='anagrafica.Appartenenza'),
        ),
        migrations.AlterField(
            model_name='estensione',
            name='destinazione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='estensioni_destinazione', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='estensione',
            name='richiedente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='estensioni_richieste_da', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='registrato_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='provvedimenti_registrati', null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='provvedimentodisciplinare',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='provvedimenti', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='riserva',
            name='appartenenza',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='riserve', to='anagrafica.Appartenenza'),
        ),
        migrations.AlterField(
            model_name='trasferimento',
            name='appartenenza',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trasferimento', blank=True, null=True, to='anagrafica.Appartenenza'),
        ),
        migrations.AlterField(
            model_name='trasferimento',
            name='destinazione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='trasferimenti_destinazione', to='anagrafica.Sede'),
        ),
        migrations.AlterField(
            model_name='trasferimento',
            name='richiedente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='trasferimenti_richiesti_da', null=True, to='anagrafica.Persona'),
        ),
    ]
