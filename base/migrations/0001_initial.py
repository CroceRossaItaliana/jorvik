# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import django_countries.fields
import base.stringhe
import anagrafica.validators
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True, blank=True, null=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), validators=[anagrafica.validators.valida_dimensione_file_10mb], verbose_name='File')),
                ('nome', models.CharField(default='File', verbose_name='Nome file', max_length=255)),
                ('oggetto_tipo', models.ForeignKey(to='contenttypes.ContentType', related_name='allegato_come_oggetto', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(base.models.ConScadenza, models.Model),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('concessa', models.NullBooleanField(db_index=True, default=None, verbose_name='Esito')),
                ('motivo_negazione', models.CharField(max_length=256, blank=True, null=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(db_index=True, default=True, verbose_name='Necessaria')),
                ('progressivo', models.PositiveSmallIntegerField(default=1, verbose_name='Progressivo contesto')),
                ('destinatario_ruolo', models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(related_name='autcomedestinatari', to='contenttypes.ContentType')),
                ('firmatario', models.ForeignKey(to='anagrafica.Persona', default=None, related_name='autorizzazioni_firmate', null=True, blank=True)),
                ('oggetto_tipo', models.ForeignKey(related_name='autcomeoggetto', to='contenttypes.ContentType')),
                ('richiedente', models.ForeignKey(related_name='autorizzazioni_richieste', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'Autorizzazioni',
            },
        ),
        migrations.CreateModel(
            name='Locazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('indirizzo', models.CharField(unique=True, verbose_name='Indirizzo', max_length=255)),
                ('geo', django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', srid=4326, blank=True)),
                ('via', models.CharField(max_length=64, blank=True, verbose_name='Via')),
                ('civico', models.CharField(max_length=16, blank=True, verbose_name='Civico')),
                ('comune', models.CharField(db_index=True, max_length=64, blank=True, verbose_name='Comune')),
                ('provincia', models.CharField(db_index=True, max_length=64, blank=True, verbose_name='Provincia')),
                ('regione', models.CharField(db_index=True, max_length=64, blank=True, verbose_name='Regione')),
                ('cap', models.CharField(db_index=True, max_length=32, blank=True, verbose_name='CAP')),
                ('stato', django_countries.fields.CountryField(default='IT', verbose_name='Stato', max_length=2)),
            ],
            options={
                'verbose_name': 'Locazione Geografica',
                'verbose_name_plural': 'Locazioni Geografiche',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
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
