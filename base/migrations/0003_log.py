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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('azione', models.CharField(max_length=1, choices=[('M', 'Modifica'), ('C', 'Creazione'), ('E', 'Eliminazione')])),
                ('oggetto_repr', models.CharField(max_length=1024, null=True, blank=True)),
                ('oggetto_app_label', models.CharField(max_length=1024, null=True, db_index=True, blank=True)),
                ('oggetto_model', models.CharField(max_length=1024, null=True, db_index=True, blank=True)),
                ('oggetto_pk', models.IntegerField(null=True, db_index=True, blank=True)),
                ('oggetto_campo', models.CharField(max_length=64, null=True, db_index=True, blank=True)),
                ('valore_precedente', models.CharField(max_length=4096, null=True, blank=True)),
                ('valore_successivo', models.CharField(max_length=4096, null=True, blank=True)),
                ('persona', models.ForeignKey(related_name='azioni_recenti', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
