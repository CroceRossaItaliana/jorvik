# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.stringhe
import django_countries.fields
import autoslug.fields
import anagrafica.models
import base.utils
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(null=True, verbose_name='Fine', default=None, blank=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('membro', models.CharField(max_length=2, verbose_name='Tipo membro', default='VO', db_index=True, choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')])),
                ('terminazione', models.CharField(null=True, default=None, db_index=True, max_length=1, verbose_name='Terminazione', choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], blank=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(null=True, verbose_name='Fine', default=None, blank=True, db_index=True)),
                ('tipo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(max_length=1, default='I', db_index=True, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')])),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('documenti/'))),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('protocollo_numero', models.PositiveIntegerField(null=True, verbose_name='Numero di protocollo', blank=True)),
                ('protocollo_data', models.DateField(null=True, verbose_name='Data di presa in carico', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('file', models.ImageField(verbose_name='Fototessera', upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'))),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=64, verbose_name='Nome')),
                ('cognome', models.CharField(max_length=64, verbose_name='Cognome')),
                ('codice_fiscale', models.CharField(max_length=16, verbose_name='Codice Fiscale', unique=True, db_index=True)),
                ('data_nascita', models.DateField(null=True, verbose_name='Data di nascita', db_index=True)),
                ('genere', models.CharField(max_length=1, verbose_name='Genere', choices=[('M', 'Maschio'), ('F', 'Femmina')], db_index=True)),
                ('stato', models.CharField(max_length=1, verbose_name='Stato', default='P', db_index=True, choices=[('P', 'Persona')])),
                ('comune_nascita', models.CharField(max_length=64, verbose_name='Comune di Nascita', blank=True)),
                ('provincia_nascita', models.CharField(max_length=2, verbose_name='Provincia di Nascita', blank=True)),
                ('stato_nascita', django_countries.fields.CountryField(max_length=2, verbose_name='Stato di nascita', default='IT')),
                ('indirizzo_residenza', models.CharField(max_length=512, verbose_name='Indirizzo di residenza', blank=True)),
                ('comune_residenza', models.CharField(max_length=64, verbose_name='Comune di residenza', blank=True)),
                ('provincia_residenza', models.CharField(max_length=2, verbose_name='Provincia di residenza', blank=True)),
                ('stato_residenza', django_countries.fields.CountryField(max_length=2, verbose_name='Stato di residenza', default='IT')),
                ('cap_residenza', models.CharField(max_length=16, verbose_name='CAP di Residenza', blank=True)),
                ('email_contatto', models.EmailField(max_length=64, verbose_name='Email di contatto', blank=True)),
                ('avatar', models.ImageField(null=True, verbose_name='Avatar', blank=True, upload_to=base.stringhe.GeneratoreNomeFile('avatar/'))),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('campo', models.CharField(max_length=8, choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')], db_index=True)),
                ('policy', models.PositiveSmallIntegerField(choices=[(8, 'Pubblico'), (6, 'Utenti di Gaia'), (4, 'A tutti i membri della mia Sede CRI'), (2, 'Ai Responsabili della mia Sede CRI'), (0, 'Solo a me')], db_index=True)),
            ],
            options={
                'verbose_name': 'Politica di Privacy',
                'verbose_name_plural': 'Politiche di Privacy',
            },
        ),
        migrations.CreateModel(
            name='ProvvedimentoDisciplinare',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('protocollo_data', models.DateField(db_index=True)),
                ('protocollo_numero', models.IntegerField()),
                ('motivazione', models.CharField(max_length=500)),
                ('tipo', models.CharField(max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=64, db_index=True)),
                ('estensione', models.CharField(max_length=1, verbose_name='Estensione', choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True)),
                ('tipo', models.CharField(max_length=1, verbose_name='Tipologia', default='C', db_index=True, choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')])),
                ('telefono', models.CharField(max_length=64, verbose_name='Telefono', blank=True)),
                ('fax', models.CharField(max_length=64, verbose_name='FAX', blank=True)),
                ('email', models.CharField(max_length=64, verbose_name='Indirizzo e-mail', blank=True)),
                ('codice_fiscale', models.CharField(max_length=32, verbose_name='Codice Fiscale', blank=True)),
                ('partita_iva', models.CharField(max_length=32, verbose_name='Partita IVA', blank=True)),
                ('slug', autoslug.fields.AutoSlugField(slugify=base.utils.sede_slugify, always_update=True, populate_from=anagrafica.models.Sede.sorgente_slug, editable=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(null=True, blank=True, related_name='figli', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Sede CRI',
                'verbose_name_plural': 'Sedi CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.CharField(max_length=16, verbose_name='Numero di telefono')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('protocollo_numero', models.PositiveIntegerField(null=True, verbose_name='Numero di protocollo', blank=True)),
                ('protocollo_data', models.DateField(null=True, verbose_name='Data di presa in carico', blank=True)),
                ('appartenenza', models.ForeignKey(related_name='trasferimento', to='anagrafica.Appartenenza')),
                ('destinazione', models.ForeignKey(related_name='trasferimenti_destinazione', to='anagrafica.Sede')),
                ('persona', models.ForeignKey(related_name='trasferimenti', to='anagrafica.Persona')),
                ('richiedente', models.ForeignKey(related_name='trasferimenti_richiesti_da', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sospensione',
            fields=[
                ('provvedimentodisciplinare_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='anagrafica.ProvvedimentoDisciplinare')),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(null=True, verbose_name='Fine', default=None, blank=True, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('anagrafica.provvedimentodisciplinare', models.Model),
        ),
    ]
