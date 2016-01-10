# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import base.stringhe
import django.contrib.gis.db.models.fields
import anagrafica.validators
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allegato',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), validators=[anagrafica.validators.valida_dimensione_file_10mb], verbose_name='File')),
                ('nome', models.CharField(max_length=255, default='File', verbose_name='Nome file')),
                ('oggetto_tipo', models.ForeignKey(blank=True, related_name='allegato_come_oggetto', null=True, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(base.models.ConScadenza, models.Model),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('concessa', models.NullBooleanField(default=None, db_index=True, verbose_name='Esito')),
                ('motivo_negazione', models.CharField(max_length=256, blank=True, null=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(default=True, db_index=True, verbose_name='Necessaria')),
                ('progressivo', models.PositiveSmallIntegerField(default=1, verbose_name='Progressivo contesto')),
                ('destinatario_ruolo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomedestinatari')),
                ('firmatario', models.ForeignKey(default=None, blank=True, null=True, related_name='autorizzazioni_firmate', to='anagrafica.Persona')),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='autcomeoggetto')),
                ('richiedente', models.ForeignKey(to='anagrafica.Persona', related_name='autorizzazioni_richieste')),
            ],
            options={
                'verbose_name_plural': 'Autorizzazioni',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('indirizzo', models.CharField(max_length=255, unique=True, verbose_name='Indirizzo')),
                ('geo', django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', blank=True, srid=4326)),
                ('via', models.CharField(max_length=64, blank=True, verbose_name='Via')),
                ('civico', models.CharField(max_length=16, blank=True, verbose_name='Civico')),
                ('comune', models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Comune')),
                ('provincia', models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Provincia')),
                ('regione', models.CharField(max_length=64, blank=True, db_index=True, verbose_name='Regione')),
                ('cap', models.CharField(max_length=32, blank=True, db_index=True, verbose_name='CAP')),
                ('stato', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato')),
            ],
            options={
                'verbose_name_plural': 'Locazioni Geografiche',
                'verbose_name': 'Locazione Geografica',
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
        migrations.CreateModel(
            name='Excel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('base.allegato',),
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('base.allegato',),
        ),
        migrations.CreateModel(
            name='Zip',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('base.allegato',),
        ),
    ]
