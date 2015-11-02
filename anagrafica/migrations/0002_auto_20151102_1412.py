# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='locazione',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='base.Locazione', related_name='anagrafica_sede', blank=True),
        ),
        migrations.AddField(
            model_name='sede',
            name='membri',
            field=models.ManyToManyField(to='anagrafica.Persona', through='anagrafica.Appartenenza'),
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
            field=models.ForeignKey(related_name='estensione', to='anagrafica.Appartenenza'),
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
            field=models.ForeignKey(to='anagrafica.Persona', related_name='deleghe_firmate', default=None, null=True, related_query_name='delega_firmata'),
        ),
        migrations.AddField(
            model_name='delega',
            name='oggetto_tipo',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='delega',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='deleghe', related_query_name='delega'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(related_name='appartenenze', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='precedente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='anagrafica.Appartenenza', related_name='successiva', default=None, blank=True),
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
