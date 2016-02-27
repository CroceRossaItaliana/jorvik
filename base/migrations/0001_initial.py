# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import anagrafica.validators
import django_countries.fields
import base.models
import base.stringhe
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True, blank=True, null=True)),
                ('file', models.FileField(validators=[anagrafica.validators.valida_dimensione_file_10mb], upload_to=base.stringhe.GeneratoreNomeFile('allegati/'), verbose_name='File')),
                ('nome', models.CharField(default='File', max_length=255, verbose_name='Nome file')),
                ('oggetto_tipo', models.ForeignKey(related_name='allegato_come_oggetto', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name_plural': 'Allegati',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Autorizzazione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('concessa', models.NullBooleanField(db_index=True, default=None, verbose_name='Esito')),
                ('motivo_negazione', models.CharField(blank=True, max_length=512, null=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('necessaria', models.BooleanField(db_index=True, default=True, verbose_name='Necessaria')),
                ('progressivo', models.PositiveSmallIntegerField(default=1, verbose_name='Progressivo contesto')),
                ('destinatario_ruolo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('GR', 'Referente Gruppo'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('destinatario_oggetto_id', models.PositiveIntegerField(db_index=True)),
                ('destinatario_oggetto_tipo', models.ForeignKey(related_name='autcomedestinatari', to='contenttypes.ContentType')),
                ('firmatario', models.ForeignKey(related_name='autorizzazioni_firmate', blank=True, default=None, to='anagrafica.Persona', null=True)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('indirizzo', models.CharField(unique=True, max_length=255, verbose_name='Indirizzo')),
                ('geo', django.contrib.gis.db.models.fields.PointField(blank=True, default='POINT(0.0 0.0)', srid=4326)),
                ('via', models.CharField(blank=True, max_length=64, verbose_name='Via')),
                ('civico', models.CharField(blank=True, max_length=16, verbose_name='Civico')),
                ('comune', models.CharField(db_index=True, max_length=64, blank=True, verbose_name='Comune')),
                ('provincia', models.CharField(db_index=True, max_length=64, blank=True, verbose_name='Provincia')),
                ('regione', models.CharField(db_index=True, max_length=64, blank=True, verbose_name='Regione')),
                ('cap', models.CharField(db_index=True, max_length=32, blank=True, verbose_name='CAP')),
                ('stato', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato')),
            ],
            options={
                'verbose_name_plural': 'Locazioni Geografiche',
                'verbose_name': 'Locazione Geografica',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('azione', models.CharField(max_length=1, choices=[('M', 'Modifica'), ('C', 'Creazione'), ('E', 'Eliminazione')])),
                ('oggetto_repr', models.CharField(blank=True, max_length=1024, null=True)),
                ('oggetto_app_label', models.CharField(db_index=True, max_length=1024, blank=True, null=True)),
                ('oggetto_model', models.CharField(db_index=True, max_length=1024, blank=True, null=True)),
                ('oggetto_pk', models.IntegerField(db_index=True, blank=True, null=True)),
                ('oggetto_campo', models.CharField(db_index=True, max_length=64, blank=True, null=True)),
                ('valore_precedente', models.CharField(blank=True, max_length=4096, null=True)),
                ('valore_successivo', models.CharField(blank=True, max_length=4096, null=True)),
                ('persona', models.ForeignKey(related_name='azioni_recenti', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
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
