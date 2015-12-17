# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Destinatario',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inviato', models.BooleanField(default=False)),
                ('tentativo', models.DateTimeField(default=None, blank=True, null=True)),
                ('errore', models.CharField(default=None, max_length=256, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Destinatario di posta',
                'verbose_name': 'Destinatario di posta',
            },
        ),
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto', models.CharField(default='(Nessun oggetto)', max_length=128, db_index=True)),
                ('corpo', models.TextField(default='(Nessun corpo)', blank=True)),
                ('ultimo_tentativo', models.DateTimeField(default=None, blank=True, null=True)),
                ('terminato', models.DateTimeField(default=None, blank=True, null=True)),
                ('mittente', models.ForeignKey(default=None, blank=True, to='anagrafica.Persona', null=True)),
            ],
            options={
                'verbose_name_plural': 'Messaggi di posta',
                'verbose_name': 'Messaggio di posta',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='messaggio',
            field=models.ForeignKey(related_name='oggetti_destinatario', blank=True, to='posta.Messaggio'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='persona',
            field=models.ForeignKey(default=None, blank=True, to='anagrafica.Persona', null=True),
        ),
    ]
