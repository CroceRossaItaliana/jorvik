# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allegato',
            name='oggetto_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='allegato_come_oggetto', blank=True, null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='autorizzazione',
            name='destinatario_oggetto_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='autcomedestinatari', null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='autorizzazione',
            name='firmatario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, related_name='autorizzazioni_firmate', blank=True, null=True, to='anagrafica.Persona'),
        ),
        migrations.AlterField(
            model_name='autorizzazione',
            name='oggetto_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='autcomeoggetto', null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='log',
            name='persona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='azioni_recenti', null=True, to='anagrafica.Persona'),
        ),
    ]
