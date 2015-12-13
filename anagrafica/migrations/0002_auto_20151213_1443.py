# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('base', '0002_auto_20151204_2015'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(default=1, related_name='appartenenze', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='precedente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, null=True, related_name='successiva', blank=True, to='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='sede',
            field=models.ForeignKey(default=1, related_name='appartenenze', to='anagrafica.Sede'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='delega',
            name='firmatario',
            field=models.ForeignKey(default=None, null=True, related_name='deleghe_firmate', related_query_name='delega_firmata', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='delega',
            name='oggetto_tipo',
            field=models.ForeignKey(default=1, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='delega',
            name='persona',
            field=models.ForeignKey(default=1, related_name='deleghe', related_query_name='delega', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dimissione',
            name='appartenenza',
            field=models.ForeignKey(default=1, related_name='dimissione', to='anagrafica.Appartenenza'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='documento',
            name='persona',
            field=models.ForeignKey(default=1, related_name='documenti', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estensione',
            name='appartenenza',
            field=models.ForeignKey(to='anagrafica.Appartenenza', null=True, related_name='estensione', blank=True),
        ),
        migrations.AddField(
            model_name='estensione',
            name='destinazione',
            field=models.ForeignKey(default=1, related_name='estensioni_destinazione', to='anagrafica.Sede'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estensione',
            name='persona',
            field=models.ForeignKey(default=1, related_name='estensioni', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estensione',
            name='richiedente',
            field=models.ForeignKey(default=1, related_name='estensioni_richieste_da', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fototessera',
            name='persona',
            field=models.ForeignKey(default=1, related_name='fototessere', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='privacy',
            name='persona',
            field=models.ForeignKey(default=1, related_name='privacy', to='anagrafica.Persona'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sede',
            name='locazione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='base.Locazione', null=True, related_name='anagrafica_sede', blank=True),
        ),
        migrations.AddField(
            model_name='sede',
            name='membri',
            field=models.ManyToManyField(to='anagrafica.Persona', through='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='trasferimento',
            name='confermata',
            field=models.BooleanField(default=True, verbose_name='Confermata', db_index=True),
        ),
        migrations.AddField(
            model_name='trasferimento',
            name='ritirata',
            field=models.BooleanField(default=False, verbose_name='Ritirata', db_index=True),
        ),
        migrations.AlterField(
            model_name='appartenenza',
            name='terminazione',
            field=models.CharField(default=None, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('FE', 'Fine Estensione')], null=True, blank=True, max_length=1, verbose_name='Terminazione', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='privacy',
            unique_together=set([('persona', 'campo')]),
        ),
    ]
