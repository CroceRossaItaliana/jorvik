# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.utils
import anagrafica.models
import django_countries.fields
import mptt.fields
import autoslug.fields
import base.stringhe


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(default=None, verbose_name='Fine', blank=True, db_index=True, null=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
                ('membro', models.CharField(choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], default='VO', verbose_name='Tipo membro', max_length=2, db_index=True)),
                ('terminazione', models.CharField(choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], default=None, null=True, blank=True, verbose_name='Terminazione', max_length=1, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(default=None, verbose_name='Fine', blank=True, db_index=True, null=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], default='I', max_length=1, db_index=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), verbose_name='File')),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), verbose_name='Fototessera')),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=64)),
                ('cognome', models.CharField(verbose_name='Cognome', max_length=64)),
                ('codice_fiscale', models.CharField(unique=True, verbose_name='Codice Fiscale', max_length=16, db_index=True)),
                ('data_nascita', models.DateField(verbose_name='Data di nascita', db_index=True, null=True)),
                ('genere', models.CharField(choices=[('M', 'Maschio'), ('F', 'Femmina')], verbose_name='Genere', max_length=1, db_index=True)),
                ('stato', models.CharField(choices=[('P', 'Persona')], default='P', verbose_name='Stato', max_length=1, db_index=True)),
                ('comune_nascita', models.CharField(verbose_name='Comune di Nascita', blank=True, max_length=64)),
                ('provincia_nascita', models.CharField(verbose_name='Provincia di Nascita', blank=True, max_length=2)),
                ('stato_nascita', django_countries.fields.CountryField(default='IT', verbose_name='Stato di nascita', max_length=2)),
                ('indirizzo_residenza', models.CharField(verbose_name='Indirizzo di residenza', blank=True, max_length=512)),
                ('comune_residenza', models.CharField(verbose_name='Comune di residenza', blank=True, max_length=64)),
                ('provincia_residenza', models.CharField(verbose_name='Provincia di residenza', blank=True, max_length=2)),
                ('stato_residenza', django_countries.fields.CountryField(default='IT', verbose_name='Stato di residenza', max_length=2)),
                ('cap_residenza', models.CharField(verbose_name='CAP di Residenza', blank=True, max_length=16)),
                ('email_contatto', models.EmailField(verbose_name='Email di contatto', blank=True, max_length=64)),
                ('avatar', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), verbose_name='Avatar', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('campo', models.CharField(choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')], max_length=8, db_index=True)),
                ('policy', models.PositiveSmallIntegerField(choices=[(8, 'Pubblico'), (6, 'Utenti di Gaia'), (4, 'A tutti i membri della mia Sede CRI'), (2, 'Ai Responsabili della mia Sede CRI'), (0, 'Solo a me')], db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Politiche di Privacy',
                'verbose_name': 'Politica di Privacy',
            },
        ),
        migrations.CreateModel(
            name='ProvvedimentoDisciplinare',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=64, db_index=True)),
                ('estensione', models.CharField(choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione', max_length=1, db_index=True)),
                ('tipo', models.CharField(choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], default='C', verbose_name='Tipologia', max_length=1, db_index=True)),
                ('telefono', models.CharField(verbose_name='Telefono', blank=True, max_length=64)),
                ('fax', models.CharField(verbose_name='FAX', blank=True, max_length=64)),
                ('email', models.CharField(verbose_name='Indirizzo e-mail', blank=True, max_length=64)),
                ('codice_fiscale', models.CharField(verbose_name='Codice Fiscale', blank=True, max_length=32)),
                ('partita_iva', models.CharField(verbose_name='Partita IVA', blank=True, max_length=32)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, populate_from=anagrafica.models.Sede.sorgente_slug, slugify=base.utils.sede_slugify, editable=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(related_name='figli', to='anagrafica.Sede', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Sedi CRI',
                'verbose_name': 'Sede CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.CharField(verbose_name='Numero di telefono', max_length=16)),
                ('servizio', models.BooleanField(default=False, verbose_name='Numero di servizio')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='numeri_telefono')),
            ],
            options={
                'verbose_name_plural': 'Numeri di telefono',
                'verbose_name': 'Numero di telefono',
            },
        ),
        migrations.CreateModel(
            name='Trasferimento',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
                ('protocollo_numero', models.PositiveIntegerField(verbose_name='Numero di protocollo', blank=True, null=True)),
                ('protocollo_data', models.DateField(verbose_name='Data di presa in carico', blank=True, null=True)),
                ('appartenenza', models.ForeignKey(to='anagrafica.Appartenenza', related_name='trasferimento')),
                ('destinazione', models.ForeignKey(to='anagrafica.Sede', related_name='trasferimenti_destinazione')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='trasferimenti')),
                ('richiedente', models.ForeignKey(to='anagrafica.Persona', related_name='trasferimenti_richiesti_da')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sospensione',
            fields=[
                ('provvedimentodisciplinare_ptr', models.OneToOneField(serialize=False, to='anagrafica.ProvvedimentoDisciplinare', parent_link=True, primary_key=True, auto_created=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(default=None, verbose_name='Fine', blank=True, db_index=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('anagrafica.provvedimentodisciplinare', models.Model),
        ),
    ]
