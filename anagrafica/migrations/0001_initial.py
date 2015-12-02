# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.stringhe
import mptt.fields
import autoslug.fields
import base.utils
import django_countries.fields
import anagrafica.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, verbose_name='Fine', null=True, blank=True, default=None)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('membro', models.CharField(db_index=True, verbose_name='Tipo membro', choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], max_length=2, default='VO')),
                ('terminazione', models.CharField(verbose_name='Terminazione', choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione')], blank=True, default=None, db_index=True, max_length=1, null=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, verbose_name='Fine', null=True, blank=True, default=None)),
                ('tipo', models.CharField(db_index=True, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
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
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(db_index=True, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], max_length=1, default='I')),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('documenti/'))),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('protocollo_numero', models.PositiveIntegerField(verbose_name='Numero di protocollo', blank=True, null=True)),
                ('protocollo_data', models.DateField(verbose_name='Data di presa in carico', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('file', models.ImageField(verbose_name='Fototessera', upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'))),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=64)),
                ('cognome', models.CharField(verbose_name='Cognome', max_length=64)),
                ('codice_fiscale', models.CharField(db_index=True, verbose_name='Codice Fiscale', max_length=16, unique=True)),
                ('data_nascita', models.DateField(db_index=True, verbose_name='Data di nascita', null=True)),
                ('genere', models.CharField(db_index=True, verbose_name='Genere', choices=[('M', 'Maschio'), ('F', 'Femmina')], max_length=1)),
                ('stato', models.CharField(db_index=True, verbose_name='Stato', choices=[('P', 'Persona')], max_length=1, default='P')),
                ('comune_nascita', models.CharField(verbose_name='Comune di Nascita', blank=True, max_length=64)),
                ('provincia_nascita', models.CharField(verbose_name='Provincia di Nascita', blank=True, max_length=2)),
                ('stato_nascita', django_countries.fields.CountryField(verbose_name='Stato di nascita', max_length=2, default='IT')),
                ('indirizzo_residenza', models.CharField(verbose_name='Indirizzo di residenza', blank=True, max_length=512)),
                ('comune_residenza', models.CharField(verbose_name='Comune di residenza', blank=True, max_length=64)),
                ('provincia_residenza', models.CharField(verbose_name='Provincia di residenza', blank=True, max_length=2)),
                ('stato_residenza', django_countries.fields.CountryField(verbose_name='Stato di residenza', max_length=2, default='IT')),
                ('cap_residenza', models.CharField(verbose_name='CAP di Residenza', blank=True, max_length=16)),
                ('email_contatto', models.EmailField(verbose_name='Email di contatto', blank=True, max_length=64)),
                ('avatar', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), verbose_name='Avatar', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('campo', models.CharField(db_index=True, choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')], max_length=8)),
                ('policy', models.PositiveSmallIntegerField(db_index=True, choices=[(8, 'Pubblico'), (6, 'Utenti di Gaia'), (4, 'A tutti i membri della mia Sede CRI'), (2, 'Ai Responsabili della mia Sede CRI'), (0, 'Solo a me')])),
            ],
            options={
                'verbose_name_plural': 'Politiche di Privacy',
                'verbose_name': 'Politica di Privacy',
            },
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, max_length=64)),
                ('estensione', models.CharField(db_index=True, verbose_name='Estensione', choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], max_length=1)),
                ('tipo', models.CharField(db_index=True, verbose_name='Tipologia', choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], max_length=1, default='C')),
                ('telefono', models.CharField(verbose_name='Telefono', blank=True, max_length=64)),
                ('fax', models.CharField(verbose_name='FAX', blank=True, max_length=64)),
                ('email', models.CharField(verbose_name='Indirizzo e-mail', blank=True, max_length=64)),
                ('codice_fiscale', models.CharField(verbose_name='Codice Fiscale', blank=True, max_length=32)),
                ('partita_iva', models.CharField(verbose_name='Partita IVA', blank=True, max_length=32)),
                ('slug', autoslug.fields.AutoSlugField(slugify=base.utils.sede_slugify, always_update=True, editable=False, populate_from=anagrafica.models.Sede.sorgente_slug)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(to='anagrafica.Sede', null=True, blank=True, related_name='figli')),
            ],
            options={
                'verbose_name_plural': 'Sedi CRI',
                'verbose_name': 'Sede CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.CharField(verbose_name='Numero di telefono', max_length=16)),
                ('servizio', models.BooleanField(verbose_name='Numero di servizio', default=False)),
                ('persona', models.ForeignKey(related_name='numeri_telefono', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Numeri di telefono',
                'verbose_name': 'Numero di telefono',
            },
        ),
        migrations.CreateModel(
            name='Trasferimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('protocollo_numero', models.PositiveIntegerField(verbose_name='Numero di protocollo', blank=True, null=True)),
                ('protocollo_data', models.DateField(verbose_name='Data di presa in carico', blank=True, null=True)),
                ('appartenenza', models.ForeignKey(related_name='trasferimento', to='anagrafica.Appartenenza')),
                ('destinazione', models.ForeignKey(related_name='trasferimenti_destinazione', to='anagrafica.Sede')),
                ('persona', models.ForeignKey(related_name='trasferimenti', to='anagrafica.Persona')),
                ('richiedente', models.ForeignKey(related_name='trasferimenti_richiesti_da', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
