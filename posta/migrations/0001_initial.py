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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inviato', models.BooleanField(default=False)),
                ('tentativo', models.DateTimeField(blank=True, default=None, null=True)),
                ('errore', models.CharField(blank=True, default=None, null=True, max_length=256)),
            ],
            options={
                'verbose_name': 'Destinatario di posta',
                'verbose_name_plural': 'Destinatario di posta',
            },
        ),
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto', models.CharField(default='(Nessun oggetto)', max_length=128, db_index=True)),
                ('corpo', models.TextField(blank=True, default='(Nessun corpo)')),
                ('ultimo_tentativo', models.DateTimeField(blank=True, default=None, null=True)),
                ('terminato', models.DateTimeField(blank=True, default=None, null=True)),
                ('mittente', models.ForeignKey(blank=True, default=None, to='anagrafica.Persona', null=True)),
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
            field=models.ForeignKey(blank=True, to='posta.Messaggio', related_name='oggetti_destinatario'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='persona',
            field=models.ForeignKey(blank=True, default=None, to='anagrafica.Persona', null=True),
        ),
    ]
