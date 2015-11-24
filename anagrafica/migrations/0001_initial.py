# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.stringhe
import autoslug.fields
import django_countries.fields
import anagrafica.models
import mptt.fields
import base.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(blank=True, verbose_name='Fine', db_index=True, default=None, null=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
                ('membro', models.CharField(choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], verbose_name='Tipo membro', max_length=2, db_index=True, default='VO')),
                ('terminazione', models.CharField(max_length=1, db_index=True, null=True, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione')], blank=True, verbose_name='Terminazione', default=None)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(blank=True, verbose_name='Fine', db_index=True, default=None, null=True)),
                ('tipo', models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], max_length=1, db_index=True, default='I')),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('documenti/'))),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
                ('protocollo_numero', models.PositiveIntegerField(blank=True, verbose_name='Numero di protocollo', null=True)),
                ('protocollo_data', models.DateField(blank=True, verbose_name='Data di presa in carico', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
                ('file', models.ImageField(verbose_name='Fototessera', upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'))),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=64)),
                ('cognome', models.CharField(verbose_name='Cognome', max_length=64)),
                ('codice_fiscale', models.CharField(unique=True, verbose_name='Codice Fiscale', max_length=16, db_index=True)),
                ('data_nascita', models.DateField(verbose_name='Data di nascita', db_index=True, null=True)),
                ('genere', models.CharField(choices=[('M', 'Maschio'), ('F', 'Femmina')], verbose_name='Genere', max_length=1, db_index=True)),
                ('stato', models.CharField(choices=[('P', 'Persona')], verbose_name='Stato', max_length=1, db_index=True, default='P')),
                ('comune_nascita', models.CharField(blank=True, verbose_name='Comune di Nascita', max_length=64)),
                ('provincia_nascita', models.CharField(blank=True, verbose_name='Provincia di Nascita', max_length=2)),
                ('stato_nascita', django_countries.fields.CountryField(verbose_name='Stato di nascita', max_length=2, default='IT')),
                ('indirizzo_residenza', models.CharField(blank=True, verbose_name='Indirizzo di residenza', max_length=512)),
                ('comune_residenza', models.CharField(blank=True, verbose_name='Comune di residenza', max_length=64)),
                ('provincia_residenza', models.CharField(blank=True, verbose_name='Provincia di residenza', max_length=2)),
                ('stato_residenza', django_countries.fields.CountryField(verbose_name='Stato di residenza', max_length=2, default='IT')),
                ('cap_residenza', models.CharField(blank=True, verbose_name='CAP di Residenza', max_length=16)),
                ('email_contatto', models.EmailField(blank=True, verbose_name='Email di contatto', max_length=64)),
                ('avatar', models.ImageField(blank=True, verbose_name='Avatar', upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), null=True)),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('campo', models.CharField(choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')], max_length=8, db_index=True)),
                ('policy', models.PositiveSmallIntegerField(choices=[(8, 'Pubblico'), (6, 'Utenti di Gaia'), (4, 'A tutti i membri della mia Sede CRI'), (2, 'Ai Responsabili della mia Sede CRI'), (0, 'Solo a me')], db_index=True)),
            ],
            options={
                'verbose_name': 'Politica di Privacy',
                'verbose_name_plural': 'Politiche di Privacy',
            },
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(max_length=64, db_index=True)),
                ('estensione', models.CharField(choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione', max_length=1, db_index=True)),
                ('tipo', models.CharField(choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], verbose_name='Tipologia', max_length=1, db_index=True, default='C')),
                ('telefono', models.CharField(blank=True, verbose_name='Telefono', max_length=64)),
                ('fax', models.CharField(blank=True, verbose_name='FAX', max_length=64)),
                ('email', models.CharField(blank=True, verbose_name='Indirizzo e-mail', max_length=64)),
                ('codice_fiscale', models.CharField(blank=True, verbose_name='Codice Fiscale', max_length=32)),
                ('partita_iva', models.CharField(blank=True, verbose_name='Partita IVA', max_length=32)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=anagrafica.models.Sede.sorgente_slug, always_update=True, slugify=base.utils.sede_slugify, editable=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(related_name='figli', to='anagrafica.Sede', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Sede CRI',
                'verbose_name_plural': 'Sedi CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.CharField(verbose_name='Numero di telefono', max_length=16)),
                ('servizio', models.BooleanField(verbose_name='Numero di servizio', default=False)),
                ('persona', models.ForeignKey(related_name='numeri_telefono', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Numero di telefono',
                'verbose_name_plural': 'Numeri di telefono',
            },
        ),
        migrations.CreateModel(
            name='Trasferimento',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('protocollo_numero', models.PositiveIntegerField(blank=True, verbose_name='Numero di protocollo', null=True)),
                ('protocollo_data', models.DateField(blank=True, verbose_name='Data di presa in carico', null=True)),
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
