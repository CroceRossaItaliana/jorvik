# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django_countries.fields
import base.models
import base.stringhe


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allegato',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), verbose_name='File')),
                ('nome', models.CharField(default='File', verbose_name='Nome file', max_length=64)),
                ('oggetto_tipo', models.ForeignKey(related_name='allegato_come_oggetto', to='contenttypes.ContentType', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(base.models.ConScadenza, models.Model),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('concessa', models.NullBooleanField(default=None, verbose_name='Esito', db_index=True)),
                ('motivo_negazione', models.CharField(max_length=256, blank=True, null=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(default=True, verbose_name='Necessaria', db_index=True)),
                ('progressivo', models.PositiveSmallIntegerField(default=1, verbose_name='Progressivo contesto')),
                ('destinatario_ruolo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomedestinatari')),
                ('firmatario', models.ForeignKey(related_name='autorizzazioni_firmate', to='anagrafica.Persona', default=None, blank=True, null=True)),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomeoggetto')),
                ('richiedente', models.ForeignKey(to='anagrafica.Persona', related_name='autorizzazioni_richieste')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'Autorizzazioni',
            },
        ),
        migrations.CreateModel(
            name='ConEstensione',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('estensione', models.CharField(choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione', max_length=1, db_index=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('indirizzo', models.CharField(unique=True, verbose_name='Indirizzo', max_length=255)),
                ('geo', django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', blank=True, srid=4326)),
                ('via', models.CharField(verbose_name='Via', blank=True, max_length=64)),
                ('civico', models.CharField(verbose_name='Civico', blank=True, max_length=16)),
                ('comune', models.CharField(verbose_name='Comune', blank=True, max_length=64, db_index=True)),
                ('provincia', models.CharField(verbose_name='Provincia', blank=True, max_length=64, db_index=True)),
                ('regione', models.CharField(verbose_name='Regione', blank=True, max_length=64, db_index=True)),
                ('cap', models.CharField(verbose_name='CAP', blank=True, max_length=32, db_index=True)),
                ('stato', django_countries.fields.CountryField(default='IT', verbose_name='Stato', max_length=2)),
            ],
            options={
                'verbose_name_plural': 'Locazioni Geografiche',
                'verbose_name': 'Locazione Geografica',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
