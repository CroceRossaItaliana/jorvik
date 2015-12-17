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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inviato', models.BooleanField(default=False)),
                ('tentativo', models.DateTimeField(null=True, default=None, blank=True)),
                ('errore', models.CharField(null=True, max_length=256, default=None, blank=True)),
            ],
            options={
                'verbose_name': 'Destinatario di posta',
                'verbose_name_plural': 'Destinatario di posta',
            },
        ),
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto', models.CharField(max_length=128, default='(Nessun oggetto)', db_index=True)),
                ('corpo', models.TextField(default='(Nessun corpo)', blank=True)),
                ('ultimo_tentativo', models.DateTimeField(null=True, default=None, blank=True)),
                ('terminato', models.DateTimeField(null=True, default=None, blank=True)),
                ('mittente', models.ForeignKey(null=True, default=None, blank=True, to='anagrafica.Persona')),
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
            field=models.ForeignKey(blank=True, related_name='oggetti_destinatario', to='posta.Messaggio'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='persona',
            field=models.ForeignKey(null=True, default=None, blank=True, to='anagrafica.Persona'),
        ),
    ]
