# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import django_countries.fields
import base.stringhe
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto_id', models.PositiveIntegerField(null=True, db_index=True, blank=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), verbose_name='File')),
                ('nome', models.CharField(max_length=64, verbose_name='Nome file', default='File')),
                ('oggetto_tipo', models.ForeignKey(blank=True, related_name='allegato_come_oggetto', to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(base.models.ConScadenza, models.Model),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('concessa', models.NullBooleanField(db_index=True, verbose_name='Esito', default=None)),
                ('motivo_negazione', models.CharField(null=True, blank=True, max_length=256)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(db_index=True, verbose_name='Necessaria', default=True)),
                ('progressivo', models.PositiveSmallIntegerField(verbose_name='Progressivo contesto', default=1)),
                ('destinatario_ruolo', models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomedestinatari')),
                ('firmatario', models.ForeignKey(blank=True, related_name='autorizzazioni_firmate', to='anagrafica.Persona', null=True, default=None)),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomeoggetto')),
                ('richiedente', models.ForeignKey(to='anagrafica.Persona', related_name='autorizzazioni_richieste')),
            ],
            options={
                'verbose_name_plural': 'Autorizzazioni',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConEstensione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('estensione', models.CharField(db_index=True, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], max_length=1, verbose_name='Estensione')),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('indirizzo', models.CharField(max_length=255, verbose_name='Indirizzo', unique=True)),
                ('geo', django.contrib.gis.db.models.fields.PointField(blank=True, srid=4326, default='POINT(0.0 0.0)')),
                ('via', models.CharField(blank=True, max_length=64, verbose_name='Via')),
                ('civico', models.CharField(blank=True, max_length=16, verbose_name='Civico')),
                ('comune', models.CharField(db_index=True, blank=True, max_length=64, verbose_name='Comune')),
                ('provincia', models.CharField(db_index=True, blank=True, max_length=64, verbose_name='Provincia')),
                ('regione', models.CharField(db_index=True, blank=True, max_length=64, verbose_name='Regione')),
                ('cap', models.CharField(db_index=True, blank=True, max_length=32, verbose_name='CAP')),
                ('stato', django_countries.fields.CountryField(max_length=2, verbose_name='Stato', default='IT')),
            ],
            options={
                'verbose_name_plural': 'Locazioni Geografiche',
                'verbose_name': 'Locazione Geografica',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
