# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.stringhe
import base.models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allegato',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('allegati/'))),
                ('nome', models.CharField(verbose_name='Nome file', max_length=64, default='File')),
                ('oggetto_tipo', models.ForeignKey(related_name='allegato_come_oggetto', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(models.Model, base.models.ConScadenza),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('concessa', models.NullBooleanField(verbose_name='Esito', db_index=True, default=None)),
                ('motivo_obbligatorio', models.BooleanField(verbose_name='Obbliga a fornire un motivo', default=False)),
                ('motivo_negazione', models.CharField(blank=True, max_length=256, null=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(verbose_name='Necessaria', db_index=True, default=True)),
                ('progressivo', models.PositiveSmallIntegerField(verbose_name='Progressivo contesto', default=1)),
                ('destinatario_ruolo', models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(related_name='autcomedestinatari', to='contenttypes.ContentType')),
                ('firmatario', models.ForeignKey(related_name='autorizzazioni_firmate', to='anagrafica.Persona', null=True, blank=True, default=None)),
                ('oggetto_tipo', models.ForeignKey(related_name='autcomeoggetto', to='contenttypes.ContentType')),
                ('richiedente', models.ForeignKey(related_name='autorizzazioni_richieste', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'Autorizzazioni',
            },
        ),
        migrations.CreateModel(
            name='ConEstensione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('estensione', models.CharField(choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione', max_length=1, db_index=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('indirizzo', models.CharField(unique=True, verbose_name='Indirizzo', max_length=255)),
                ('geo', django.contrib.gis.db.models.fields.PointField(blank=True, srid=4326, default='POINT(0.0 0.0)')),
                ('via', models.CharField(blank=True, verbose_name='Via', max_length=64)),
                ('civico', models.CharField(blank=True, verbose_name='Civico', max_length=16)),
                ('comune', models.CharField(blank=True, verbose_name='Comune', max_length=64, db_index=True)),
                ('provincia', models.CharField(blank=True, verbose_name='Provincia', max_length=64, db_index=True)),
                ('regione', models.CharField(blank=True, verbose_name='Regione', max_length=64, db_index=True)),
                ('cap', models.CharField(blank=True, verbose_name='CAP', max_length=32, db_index=True)),
                ('stato', models.CharField(blank=True, verbose_name='Stato', max_length=2, db_index=True)),
            ],
            options={
                'verbose_name': 'Locazione Geografica',
                'verbose_name_plural': 'Locazioni Geografiche',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
