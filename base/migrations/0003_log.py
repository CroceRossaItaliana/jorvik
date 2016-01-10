# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0007_auto_20160111_0047'),
        ('base', '0002_auto_20160110_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('azione', models.CharField(max_length=1, choices=[('M', 'Modifica'), ('C', 'Creazione'), ('E', 'Eliminazione')])),
                ('oggetto_repr', models.CharField(blank=True, null=True, max_length=1024)),
                ('oggetto_app_label', models.CharField(blank=True, null=True, max_length=1024, db_index=True)),
                ('oggetto_model', models.CharField(blank=True, null=True, max_length=1024, db_index=True)),
                ('oggetto_pk', models.IntegerField(blank=True, null=True, db_index=True)),
                ('oggetto_campo', models.CharField(blank=True, null=True, max_length=64, db_index=True)),
                ('valore_precedente', models.CharField(blank=True, null=True, max_length=4096)),
                ('valore_successivo', models.CharField(blank=True, null=True, max_length=4096)),
                ('persona', models.ForeignKey(to_field='azioni_recenti', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
