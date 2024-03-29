# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-11-18 14:21
from __future__ import unicode_literals

import anagrafica.validators
import base.stringhe
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0062_auto_20201113_1059'),
        ('gestione_file', '0009_documentosegmento_sedi_sottostanti'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoComitato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(choices=[('CATEGORIA1', (('NOME1', 'NOME1'), ('NOME2', 'NOME2'))), ('CATEGORIA1', (('NOME3', 'NOME3'), ('NOME4', 'NOME4')))], max_length=50)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='File')),
                ('expires', models.DateField(null=True)),
                ('sede', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Documenti Comitato',
                'verbose_name_plural': 'Documenti Comitato',
            },
        ),
    ]
