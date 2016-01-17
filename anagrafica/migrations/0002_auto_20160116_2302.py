# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='locazione',
            field=models.ForeignKey(related_name='anagrafica_sede', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Locazione', null=True),
        ),
        migrations.AddField(
            model_name='sede',
            name='membri',
            field=models.ManyToManyField(through='anagrafica.Appartenenza', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='persona',
            field=models.ForeignKey(related_name='provvedimenti', to='anagrafica.Persona'),
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
            field=models.ForeignKey(related_name='estensione', blank=True, to='anagrafica.Appartenenza', null=True),
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
            field=models.ForeignKey(related_name='dimissioni', to='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='dimissione',
            name='persona',
            field=models.ForeignKey(related_name='dimissioni', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='dimissione',
            name='richiedente',
            field=models.ForeignKey(to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='dimissione',
            name='sede',
            field=models.ForeignKey(related_name='dimissioni', to='anagrafica.Sede'),
        ),
        migrations.AddField(
            model_name='delega',
            name='firmatario',
            field=models.ForeignKey(related_name='deleghe_firmate', related_query_name='delega_firmata', default=None, to='anagrafica.Persona', null=True),
        ),
        migrations.AddField(
            model_name='delega',
            name='oggetto_tipo',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='delega',
            name='persona',
            field=models.ForeignKey(related_name='deleghe', related_query_name='delega', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='persona',
            field=models.ForeignKey(related_name='appartenenze', to='anagrafica.Persona'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='precedente',
            field=models.ForeignKey(related_name='successiva', on_delete=django.db.models.deletion.SET_NULL, blank=True, default=None, to='anagrafica.Appartenenza', null=True),
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
