# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.stringhe
import django.contrib.gis.db.models.fields
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allegato',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(null=True, blank=True, db_index=True)),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('allegati/'))),
                ('nome', models.CharField(max_length=64, verbose_name='Nome file', default='File')),
                ('oggetto_tipo', models.ForeignKey(null=True, blank=True, related_name='allegato_come_oggetto', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(base.models.ConScadenza, models.Model),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('concessa', models.NullBooleanField(verbose_name='Esito', default=None, db_index=True)),
                ('motivo_obbligatorio', models.BooleanField(verbose_name='Obbliga a fornire un motivo', default=False)),
                ('motivo_negazione', models.CharField(null=True, max_length=256, blank=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(verbose_name='Necessaria', default=True, db_index=True)),
                ('progressivo', models.PositiveSmallIntegerField(verbose_name='Progressivo contesto', default=1)),
                ('destinatario_ruolo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(related_name='autcomedestinatari', to='contenttypes.ContentType')),
                ('firmatario', models.ForeignKey(null=True, default=None, blank=True, related_name='autorizzazioni_firmate', to='anagrafica.Persona')),
                ('oggetto_tipo', models.ForeignKey(related_name='autcomeoggetto', to='contenttypes.ContentType')),
                ('richiedente', models.ForeignKey(related_name='autorizzazioni_richieste', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Autorizzazioni',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConEstensione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('estensione', models.CharField(max_length=1, verbose_name='Estensione', choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('indirizzo', models.CharField(max_length=255, verbose_name='Indirizzo', unique=True)),
                ('geo', django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', blank=True, srid=4326)),
                ('via', models.CharField(max_length=64, verbose_name='Via', blank=True)),
                ('civico', models.CharField(max_length=16, verbose_name='Civico', blank=True)),
                ('comune', models.CharField(max_length=64, verbose_name='Comune', blank=True, db_index=True)),
                ('provincia', models.CharField(max_length=64, verbose_name='Provincia', blank=True, db_index=True)),
                ('regione', models.CharField(max_length=64, verbose_name='Regione', blank=True, db_index=True)),
                ('cap', models.CharField(max_length=32, verbose_name='CAP', blank=True, db_index=True)),
                ('stato', models.CharField(max_length=2, verbose_name='Stato', blank=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Locazione Geografica',
                'verbose_name_plural': 'Locazioni Geografiche',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
