# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='locazione',
            field=models.ForeignKey(related_name='anagrafica_sede', blank=True, null=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='sede',
            name='membri',
            field=models.ManyToManyField(through='anagrafica.Appartenenza', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='privacy',
            name='persona',
            field=models.ForeignKey(related_name='privacy', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='fototessera',
            name='persona',
            field=models.ForeignKey(related_name='fototessere', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='appartenenza',
            field=models.ForeignKey(related_name='estensione', blank=True, null=True, to='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='destinazione',
            field=models.ForeignKey(related_name='estensioni_destinazione', to='anagrafica.Sede'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='persona',
            field=models.ForeignKey(related_name='estensioni', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='richiedente',
            field=models.ForeignKey(related_name='estensioni_richieste_da', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='documento',
            name='persona',
            field=models.ForeignKey(related_name='documenti', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='dimissione',
            name='appartenenza',
            field=models.ForeignKey(related_name='dimissione', to='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='delega',
            name='firmatario',
            field=models.ForeignKey(related_query_name='delega_firmata', related_name='deleghe_firmate', default=None, null=True, to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='delega',
            name='oggetto_tipo',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='delega',
            name='persona',
            field=models.ForeignKey(related_query_name='delega', related_name='deleghe', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(related_name='appartenenze', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='precedente',
            field=models.ForeignKey(related_name='successiva', default=None, blank=True, null=True, to='anagrafica.Appartenenza', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='sede',
            field=models.ForeignKey(related_name='appartenenze', to='anagrafica.Sede'),
        ),
        migrations.AlterUniqueTogether(
            name='privacy',
            unique_together=set([('persona', 'campo')]),
        ),
    ]
