# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import django.contrib.gis.db.models.fields
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto_id', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), verbose_name='File')),
                ('nome', models.CharField(default='File', max_length=64, verbose_name='Nome file')),
                ('oggetto_tipo', models.ForeignKey(related_name='allegato_come_oggetto', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(base.models.ConScadenza, models.Model),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('concessa', models.NullBooleanField(default=None, verbose_name='Esito', db_index=True)),
                ('motivo_negazione', models.CharField(max_length=256, blank=True, null=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(default=True, db_index=True, verbose_name='Necessaria')),
                ('progressivo', models.PositiveSmallIntegerField(default=1, verbose_name='Progressivo contesto')),
                ('destinatario_ruolo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomedestinatari')),
                ('firmatario', models.ForeignKey(default=None, related_name='autorizzazioni_firmate', blank=True, to='anagrafica.Persona', null=True)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('estensione', models.CharField(max_length=1, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True, verbose_name='Estensione')),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('indirizzo', models.CharField(max_length=255, unique=True, verbose_name='Indirizzo')),
                ('geo', django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', srid=4326, blank=True)),
                ('via', models.CharField(max_length=64, blank=True, verbose_name='Via')),
                ('civico', models.CharField(max_length=16, blank=True, verbose_name='Civico')),
                ('comune', models.CharField(max_length=64, db_index=True, blank=True, verbose_name='Comune')),
                ('provincia', models.CharField(max_length=64, db_index=True, blank=True, verbose_name='Provincia')),
                ('regione', models.CharField(max_length=64, db_index=True, blank=True, verbose_name='Regione')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
