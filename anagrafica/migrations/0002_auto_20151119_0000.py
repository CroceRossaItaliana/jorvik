# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('base', '0001_initial'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='locazione',
            field=models.ForeignKey(blank=True, to='base.Locazione', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='anagrafica_sede'),
        ),
        migrations.AddField(
            model_name='sede',
            name='membri',
            field=models.ManyToManyField(to='anagrafica.Persona', through='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='privacy',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='privacy'),
        ),
        migrations.AddField(
            model_name='fototessera',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='fototessere'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='appartenenza',
            field=models.ForeignKey(blank=True, to='anagrafica.Appartenenza', null=True, related_name='estensione'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='destinazione',
            field=models.ForeignKey(to='anagrafica.Sede', related_name='estensioni_destinazione'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='richiedente',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='richiedente'),
        ),
        migrations.AddField(
            model_name='documento',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='documenti'),
        ),
        migrations.AddField(
            model_name='dimissione',
            name='appartenenza',
            field=models.ForeignKey(to='anagrafica.Appartenenza', related_name='dimissione'),
        ),
        migrations.AddField(
            model_name='delega',
            name='firmatario',
            field=models.ForeignKey(related_query_name='delega_firmata', default=None, to='anagrafica.Persona', null=True, related_name='deleghe_firmate'),
        ),
        migrations.AddField(
            model_name='delega',
            name='oggetto_tipo',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='delega',
            name='persona',
            field=models.ForeignKey(related_query_name='delega', to='anagrafica.Persona', related_name='deleghe'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='appartenenze'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='precedente',
            field=models.ForeignKey(to='anagrafica.Appartenenza', blank=True, default=None, on_delete=django.db.models.deletion.SET_NULL, related_name='successiva', null=True),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='sede',
            field=models.ForeignKey(to='anagrafica.Sede', related_name='appartenenze'),
        ),
        migrations.AlterUniqueTogether(
            name='privacy',
            unique_together=set([('persona', 'campo')]),
        ),
    ]
