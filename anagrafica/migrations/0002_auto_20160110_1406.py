# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sede',
            name='locazione',
            field=models.ForeignKey(to='base.Locazione', related_name='anagrafica_sede', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sede',
            name='membri',
            field=models.ManyToManyField(to='anagrafica.Persona', through='anagrafica.Appartenenza'),
        ),
        migrations.AddField(
            model_name='provvedimentodisciplinare',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='provvedimenti'),
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
            field=models.ForeignKey(to='anagrafica.Appartenenza', related_name='estensione', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='estensione',
            name='destinazione',
            field=models.ForeignKey(to='anagrafica.Sede', related_name='estensioni_destinazione'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='estensioni'),
        ),
        migrations.AddField(
            model_name='estensione',
            name='richiedente',
            field=models.ForeignKey(to='anagrafica.Persona', related_name='estensioni_richieste_da'),
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
            field=models.ForeignKey(related_query_name='delega_firmata', to='anagrafica.Persona', related_name='deleghe_firmate', default=None, null=True),
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
            field=models.ForeignKey(to='anagrafica.Persona', related_name='appartenenze'),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='precedente',
            field=models.ForeignKey(to='anagrafica.Appartenenza', related_name='successiva', null=True, on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True),
        ),
        migrations.AddField(
            model_name='appartenenza',
            name='sede',
            field=models.ForeignKey(to='anagrafica.Sede', related_name='appartenenze'),
        ),
        migrations.AddField(
            model_name='sospensione',
            name='provvedimento',
            field=models.ForeignKey(to='anagrafica.ProvvedimentoDisciplinare', related_name='provvedimento'),
        ),
        migrations.AlterUniqueTogether(
            name='privacy',
            unique_together=set([('persona', 'campo')]),
        ),
    ]
