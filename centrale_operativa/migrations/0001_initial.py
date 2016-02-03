# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0031_auto_20160203_0311'),
        ('attivita', '0009_auto_20160129_0109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reperibilita',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('creazione', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(null=True, default=None, verbose_name='Fine', blank=True, db_index=True)),
                ('attivazione', models.TimeField(default='00:15', help_text="Tempo necessario all'attivazione, in formato HH:mm.", verbose_name='Tempo di attivazione')),
                ('persona', models.ForeignKey(related_name='reperibilita', to='anagrafica.Persona')),
            ],
            options={
                'ordering': ['-inizio', '-fine'],
                'verbose_name': 'Reperibilità',
                'verbose_name_plural': 'Reperibilità',
            },
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('creazione', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('montato_data', models.DateTimeField(null=True)),
                ('smontato_data', models.DateTimeField(null=True)),
                ('montato_da', models.ForeignKey(related_name='coturni_montati', null=True, default=None, to='anagrafica.Persona')),
                ('persona', models.ForeignKey(related_name='coturni', to='anagrafica.Persona')),
                ('smontato_da', models.ForeignKey(related_name='coturni_smontati', null=True, default=None, to='anagrafica.Persona')),
                ('turno', models.ForeignKey(related_name='coturni', to='attivita.Turno')),
            ],
            options={
                'verbose_name': 'Turno',
                'verbose_name_plural': 'Turni',
            },
        ),
        migrations.AlterIndexTogether(
            name='turno',
            index_together=set([('persona', 'turno')]),
        ),
    ]
