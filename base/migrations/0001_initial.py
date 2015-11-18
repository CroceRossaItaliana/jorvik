# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.stringhe
import base.models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allegato',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('allegati/'))),
                ('nome', models.CharField(verbose_name='Nome file', default='File', max_length=64)),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='allegato_come_oggetto')),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(models.Model, base.models.ConScadenza),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('concessa', models.NullBooleanField(verbose_name='Esito', default=None, db_index=True)),
                ('motivo_obbligatorio', models.BooleanField(verbose_name='Obbliga a fornire un motivo', default=False)),
                ('motivo_negazione', models.CharField(blank=True, null=True, max_length=256)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(verbose_name='Necessaria', default=True, db_index=True)),
                ('progressivo', models.PositiveSmallIntegerField(verbose_name='Progressivo contesto', default=1)),
                ('destinatario_ruolo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomedestinatari')),
                ('firmatario', models.ForeignKey(blank=True, default=None, to='anagrafica.Persona', related_name='autorizzazioni_firmate', null=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('estensione', models.CharField(verbose_name='Estensione', max_length=1, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('indirizzo', models.CharField(verbose_name='Indirizzo', unique=True, max_length=255)),
                ('geo', django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True, default='POINT(0.0 0.0)')),
                ('via', models.CharField(verbose_name='Via', blank=True, max_length=64)),
                ('civico', models.CharField(verbose_name='Civico', blank=True, max_length=8)),
                ('comune', models.CharField(verbose_name='Comune', blank=True, max_length=64, db_index=True)),
                ('provincia', models.CharField(verbose_name='Provincia', blank=True, max_length=32, db_index=True)),
                ('regione', models.CharField(verbose_name='Regione', blank=True, max_length=32, db_index=True)),
                ('cap', models.CharField(verbose_name='CAP', blank=True, max_length=32, db_index=True)),
                ('stato', models.CharField(verbose_name='Stato', blank=True, max_length=2, db_index=True)),
            ],
            options={
                'verbose_name': 'Locazione Geografica',
                'verbose_name_plural': 'Locazioni Geografiche',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
