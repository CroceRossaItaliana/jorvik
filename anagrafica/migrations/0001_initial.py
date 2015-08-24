# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import anagrafica.models
import base.utils
import base.stringhe
import django_countries.fields
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, default=None, blank=True, verbose_name='Fine', null=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('membro', models.CharField(db_index=True, default='VO', verbose_name='Tipo membro', choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], max_length=2)),
                ('terminazione', models.CharField(db_index=True, default=None, blank=True, verbose_name='Terminazione', null=True, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento')], max_length=1)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, default=None, blank=True, verbose_name='Fine', null=True)),
                ('tipo', models.CharField(db_index=True, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('DA', "Delegato d'Area"), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività')], max_length=2)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(db_index=True, default='I', choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], max_length=1)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), verbose_name='File')),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), verbose_name='Fototessera')),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('nome', models.CharField(verbose_name='Nome', max_length=64)),
                ('cognome', models.CharField(verbose_name='Cognome', max_length=64)),
                ('codice_fiscale', models.CharField(db_index=True, unique=True, verbose_name='Codice Fiscale', max_length=16)),
                ('data_nascita', models.DateField(db_index=True, verbose_name='Data di nascita')),
                ('genere', models.CharField(db_index=True, verbose_name='Genere', choices=[('M', 'Maschio'), ('F', 'Femmina')], max_length=1)),
                ('stato', models.CharField(db_index=True, default='P', verbose_name='Stato', choices=[('P', 'Persona')], max_length=1)),
                ('comune_nascita', models.CharField(blank=True, verbose_name='Comune di Nascita', max_length=64)),
                ('provincia_nascita', models.CharField(blank=True, verbose_name='Provincia di Nascita', max_length=2)),
                ('stato_nascita', django_countries.fields.CountryField(default='IT', verbose_name='Stato di nascita', max_length=2)),
                ('indirizzo_residenza', models.CharField(blank=True, verbose_name='Indirizzo di residenza', max_length=64)),
                ('comune_residenza', models.CharField(blank=True, verbose_name='Comune di residenza', max_length=64)),
                ('provincia_residenza', models.CharField(blank=True, verbose_name='Provincia di residenza', max_length=2)),
                ('stato_residenza', django_countries.fields.CountryField(default='IT', verbose_name='Stato di residenza', max_length=2)),
                ('cap_residenza', models.CharField(blank=True, verbose_name='CAP di Residenza', max_length=8)),
                ('email_contatto', models.CharField(blank=True, verbose_name='Email di contatto', max_length=64)),
                ('avatar', models.ImageField(null=True, blank=True, verbose_name='Avatar', upload_to=base.stringhe.GeneratoreNomeFile('avatar/'))),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, max_length=64)),
                ('estensione', models.CharField(db_index=True, verbose_name='Estensione', choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], max_length=1)),
                ('tipo', models.CharField(db_index=True, default='C', verbose_name='Tipologia', choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], max_length=1)),
                ('telefono', models.CharField(blank=True, verbose_name='Telefono', max_length=64)),
                ('fax', models.CharField(blank=True, verbose_name='FAX', max_length=64)),
                ('email', models.CharField(blank=True, verbose_name='Indirizzo e-mail', max_length=64)),
                ('codice_fiscale', models.CharField(blank=True, verbose_name='Codice Fiscale', max_length=32)),
                ('partita_iva', models.CharField(blank=True, verbose_name='Partita IVA', max_length=32)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=anagrafica.models.Sede.sorgente_slug, editable=False, always_update=True, slugify=base.utils.sede_slugify)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.CharField(verbose_name='Numero di telefono', max_length=16)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('appartenenza', models.ForeignKey(related_name='trasferimento', to='anagrafica.Appartenenza')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
