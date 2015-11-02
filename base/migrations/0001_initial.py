# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), verbose_name='File')),
                ('nome', models.CharField(default='File', max_length=64, verbose_name='Nome file')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('concessa', models.NullBooleanField(db_index=True, default=None, verbose_name='Esito')),
                ('motivo_obbligatorio', models.BooleanField(default=False, verbose_name='Obbliga a fornire un motivo')),
                ('motivo_negazione', models.CharField(null=True, blank=True, max_length=256)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(default=True, db_index=True, verbose_name='Necessaria')),
                ('progressivo', models.PositiveSmallIntegerField(default=1, verbose_name='Progressivo contesto')),
                ('destinatario_ruolo', models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(related_name='autcomedestinatari', to='contenttypes.ContentType')),
                ('firmatario', models.ForeignKey(null=True, to='anagrafica.Persona', related_name='autorizzazioni_firmate', default=None, blank=True)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estensione', models.CharField(max_length=1, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True, verbose_name='Estensione')),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('indirizzo', models.CharField(max_length=255, unique=True, verbose_name='Indirizzo')),
                ('geo', django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', blank=True, srid=4326)),
                ('via', models.CharField(max_length=64, blank=True, verbose_name='Via')),
                ('civico', models.CharField(max_length=8, blank=True, verbose_name='Civico')),
                ('comune', models.CharField(max_length=64, db_index=True, blank=True, verbose_name='Comune')),
                ('provincia', models.CharField(max_length=32, db_index=True, blank=True, verbose_name='Provincia')),
                ('regione', models.CharField(max_length=32, db_index=True, blank=True, verbose_name='Regione')),
                ('cap', models.CharField(max_length=32, db_index=True, blank=True, verbose_name='CAP')),
                ('stato', models.CharField(max_length=2, db_index=True, blank=True, verbose_name='Stato')),
            ],
            options={
                'verbose_name_plural': 'Locazioni Geografiche',
                'verbose_name': 'Locazione Geografica',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
