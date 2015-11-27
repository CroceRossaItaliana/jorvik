# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Destinatario',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inviato', models.BooleanField(default=False)),
                ('tentativo', models.DateTimeField(blank=True, default=None, null=True)),
                ('errore', models.CharField(blank=True, max_length=256, default=None, null=True)),
            ],
            options={
                'verbose_name': 'Destinatario di posta',
                'verbose_name_plural': 'Destinatario di posta',
            },
        ),
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto', models.CharField(max_length=128, db_index=True, default='(Nessun oggetto)')),
                ('corpo', models.TextField(blank=True, default='(Nessun corpo)')),
                ('ultimo_tentativo', models.DateTimeField(blank=True, default=None, null=True)),
                ('terminato', models.DateTimeField(blank=True, default=None, null=True)),
                ('mittente', models.ForeignKey(to='anagrafica.Persona', null=True, blank=True, default=None)),
            ],
            options={
                'verbose_name': 'Messaggio di posta',
                'verbose_name_plural': 'Messaggi di posta',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='messaggio',
            field=models.ForeignKey(related_name='oggetti_destinatario', to='posta.Messaggio', blank=True),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', null=True, blank=True, default=None),
        ),
    ]
