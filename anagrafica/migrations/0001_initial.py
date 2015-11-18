# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.utils
import anagrafica.models
import mptt.fields
import autoslug.fields
import base.stringhe
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(default=None, blank=True, db_index=True, null=True, verbose_name='Fine')),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('membro', models.CharField(default='VO', db_index=True, max_length=2, verbose_name='Tipo membro', choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')])),
                ('terminazione', models.CharField(default=None, blank=True, db_index=True, max_length=1, null=True, verbose_name='Terminazione', choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione')])),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(default=None, blank=True, db_index=True, null=True, verbose_name='Fine')),
                ('tipo', models.CharField(db_index=True, max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(default='I', db_index=True, max_length=1, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')])),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), verbose_name='File')),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('protocollo_numero', models.PositiveIntegerField(blank=True, null=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(blank=True, null=True, verbose_name='Data di presa in carico')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), verbose_name='Fototessera')),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(max_length=64, verbose_name='Nome')),
                ('cognome', models.CharField(max_length=64, verbose_name='Cognome')),
                ('codice_fiscale', models.CharField(unique=True, db_index=True, max_length=16, verbose_name='Codice Fiscale')),
                ('data_nascita', models.DateField(db_index=True, null=True, verbose_name='Data di nascita')),
                ('genere', models.CharField(db_index=True, max_length=1, verbose_name='Genere', choices=[('M', 'Maschio'), ('F', 'Femmina')])),
                ('stato', models.CharField(default='P', db_index=True, max_length=1, verbose_name='Stato', choices=[('P', 'Persona')])),
                ('comune_nascita', models.CharField(blank=True, max_length=64, verbose_name='Comune di Nascita')),
                ('provincia_nascita', models.CharField(blank=True, max_length=2, verbose_name='Provincia di Nascita')),
                ('stato_nascita', django_countries.fields.CountryField(default='IT', max_length=2, verbose_name='Stato di nascita')),
                ('indirizzo_residenza', models.CharField(blank=True, max_length=256, verbose_name='Indirizzo di residenza')),
                ('comune_residenza', models.CharField(blank=True, max_length=64, verbose_name='Comune di residenza')),
                ('provincia_residenza', models.CharField(blank=True, max_length=2, verbose_name='Provincia di residenza')),
                ('stato_residenza', django_countries.fields.CountryField(default='IT', max_length=2, verbose_name='Stato di residenza')),
                ('cap_residenza', models.CharField(blank=True, max_length=16, verbose_name='CAP di Residenza')),
                ('email_contatto', models.EmailField(blank=True, max_length=64, verbose_name='Email di contatto')),
                ('avatar', models.ImageField(blank=True, null=True, verbose_name='Avatar', upload_to=base.stringhe.GeneratoreNomeFile('avatar/'))),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('campo', models.CharField(db_index=True, max_length=8, choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')])),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, max_length=64)),
                ('estensione', models.CharField(db_index=True, max_length=1, verbose_name='Estensione', choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')])),
                ('tipo', models.CharField(default='C', db_index=True, max_length=1, verbose_name='Tipologia', choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')])),
                ('telefono', models.CharField(blank=True, max_length=64, verbose_name='Telefono')),
                ('fax', models.CharField(blank=True, max_length=64, verbose_name='FAX')),
                ('email', models.CharField(blank=True, max_length=64, verbose_name='Indirizzo e-mail')),
                ('codice_fiscale', models.CharField(blank=True, max_length=32, verbose_name='Codice Fiscale')),
                ('partita_iva', models.CharField(blank=True, max_length=32, verbose_name='Partita IVA')),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, slugify=base.utils.sede_slugify, populate_from=anagrafica.models.Sede.sorgente_slug)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(blank=True, null=True, related_name='figli', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Sedi CRI',
                'verbose_name': 'Sede CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.CharField(max_length=16, verbose_name='Numero di telefono')),
                ('servizio', models.BooleanField(default=False, verbose_name='Numero di servizio')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('appartenenza', models.ForeignKey(related_name='trasferimento', to='anagrafica.Appartenenza')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
