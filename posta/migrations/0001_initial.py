# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0002_auto_20151102_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='Destinatario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inviato', models.BooleanField(default=False)),
                ('tentativo', models.DateTimeField(default=None, null=True, blank=True)),
                ('errore', models.CharField(default=None, blank=True, null=True, max_length=256)),
            ],
            options={
                'verbose_name': 'Destinatario di posta',
                'verbose_name_plural': 'Destinatario di posta',
            },
        ),
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto', models.CharField(default='(Nessun oggetto)', max_length=128, db_index=True)),
                ('corpo', models.TextField(default='(Nessun corpo)', blank=True)),
                ('ultimo_tentativo', models.DateTimeField(default=None, null=True, blank=True)),
                ('terminato', models.DateTimeField(default=None, null=True, blank=True)),
                ('mittente', models.ForeignKey(default=None, to='anagrafica.Persona', null=True, blank=True)),
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
            field=models.ForeignKey(default=None, to='anagrafica.Persona', null=True, blank=True),
        ),
    ]
