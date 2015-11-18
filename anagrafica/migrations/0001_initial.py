# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import mptt.fields
import base.utils
import anagrafica.models
import base.stringhe
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(verbose_name='Fine', blank=True, default=None, null=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('membro', models.CharField(verbose_name='Tipo membro', default='VO', max_length=2, choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], db_index=True)),
                ('terminazione', models.CharField(blank=True, default=None, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione')], verbose_name='Terminazione', null=True, max_length=1, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(verbose_name='Fine', blank=True, default=None, null=True, db_index=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(default='I', max_length=1, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], db_index=True)),
                ('file', models.FileField(verbose_name='File', upload_to=base.stringhe.GeneratoreNomeFile('documenti/'))),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=64)),
                ('cognome', models.CharField(verbose_name='Cognome', max_length=64)),
                ('codice_fiscale', models.CharField(verbose_name='Codice Fiscale', unique=True, max_length=16, db_index=True)),
                ('data_nascita', models.DateField(verbose_name='Data di nascita', null=True, db_index=True)),
                ('genere', models.CharField(verbose_name='Genere', max_length=1, choices=[('M', 'Maschio'), ('F', 'Femmina')], db_index=True)),
                ('stato', models.CharField(verbose_name='Stato', default='P', max_length=1, choices=[('P', 'Persona')], db_index=True)),
                ('comune_nascita', models.CharField(verbose_name='Comune di Nascita', blank=True, max_length=64)),
                ('provincia_nascita', models.CharField(verbose_name='Provincia di Nascita', blank=True, max_length=2)),
                ('stato_nascita', django_countries.fields.CountryField(verbose_name='Stato di nascita', default='IT', max_length=2)),
                ('indirizzo_residenza', models.CharField(verbose_name='Indirizzo di residenza', blank=True, max_length=256)),
                ('comune_residenza', models.CharField(verbose_name='Comune di residenza', blank=True, max_length=64)),
                ('provincia_residenza', models.CharField(verbose_name='Provincia di residenza', blank=True, max_length=2)),
                ('stato_residenza', django_countries.fields.CountryField(verbose_name='Stato di residenza', default='IT', max_length=2)),
                ('cap_residenza', models.CharField(verbose_name='CAP di Residenza', blank=True, max_length=16)),
                ('email_contatto', models.EmailField(verbose_name='Email di contatto', blank=True, max_length=64)),
                ('avatar', models.ImageField(verbose_name='Avatar', blank=True, null=True, upload_to=base.stringhe.GeneratoreNomeFile('avatar/'))),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
            name='Sede',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=64, db_index=True)),
                ('estensione', models.CharField(verbose_name='Estensione', max_length=1, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True)),
                ('tipo', models.CharField(verbose_name='Tipologia', default='C', max_length=1, choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], db_index=True)),
                ('telefono', models.CharField(verbose_name='Telefono', blank=True, max_length=64)),
                ('fax', models.CharField(verbose_name='FAX', blank=True, max_length=64)),
                ('email', models.CharField(verbose_name='Indirizzo e-mail', blank=True, max_length=64)),
                ('codice_fiscale', models.CharField(verbose_name='Codice Fiscale', blank=True, max_length=32)),
                ('partita_iva', models.CharField(verbose_name='Partita IVA', blank=True, max_length=32)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=anagrafica.models.Sede.sorgente_slug, editable=False, always_update=True, slugify=base.utils.sede_slugify)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('genitore', mptt.fields.TreeForeignKey(blank=True, to='anagrafica.Sede', null=True, related_name='figli')),
            ],
            options={
                'verbose_name': 'Sede CRI',
                'verbose_name_plural': 'Sedi CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.CharField(verbose_name='Numero di telefono', max_length=16)),
                ('servizio', models.BooleanField(verbose_name='Numero di servizio', default=False)),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='numeri_telefono')),
            ],
            options={
                'verbose_name': 'Numero di telefono',
                'verbose_name_plural': 'Numeri di telefono',
            },
        ),
        migrations.CreateModel(
            name='Trasferimento',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('appartenenza', models.ForeignKey(to='anagrafica.Appartenenza', related_name='trasferimento')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
