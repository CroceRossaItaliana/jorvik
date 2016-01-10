# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.stringhe
import mptt.fields
import base.utils
import anagrafica.models
import autoslug.fields
import anagrafica.validators
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
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, blank=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, verbose_name='Fine', db_index=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('membro', models.CharField(max_length=2, default='VO', choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], db_index=True, verbose_name='Tipo membro')),
                ('terminazione', models.CharField(max_length=1, default=None, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], null=True, verbose_name='Terminazione', db_index=True, blank=True)),
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
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, blank=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, verbose_name='Fine', db_index=True)),
                ('tipo', models.CharField(max_length=2, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], db_index=True)),
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
                ('tipo', models.CharField(max_length=1, default='I', db_index=True, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')])),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='File')),
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
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('protocollo_numero', models.PositiveIntegerField(blank=True, null=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(blank=True, null=True, verbose_name='Data di presa in carico')),
                ('attuale', models.CharField(max_length=1, default='s', verbose_name='Attualità della richiesta')),
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
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='Fototessera')),
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
                ('vecchio_id', models.IntegerField(default=None, blank=True, null=True, db_index=True)),
                ('nome', models.CharField(max_length=64, verbose_name='Nome')),
                ('cognome', models.CharField(max_length=64, verbose_name='Cognome')),
                ('codice_fiscale', models.CharField(max_length=16, db_index=True, validators=[anagrafica.validators.valida_codice_fiscale], unique=True, verbose_name='Codice Fiscale')),
                ('data_nascita', models.DateField(db_index=True, null=True, verbose_name='Data di nascita')),
                ('genere', models.CharField(max_length=1, choices=[('M', 'Maschio'), ('F', 'Femmina')], db_index=True, verbose_name='Genere')),
                ('stato', models.CharField(max_length=1, default='P', choices=[('P', 'Persona')], db_index=True, verbose_name='Stato')),
                ('comune_nascita', models.CharField(max_length=64, blank=True, verbose_name='Comune di Nascita')),
                ('provincia_nascita', models.CharField(max_length=2, blank=True, verbose_name='Provincia di Nascita')),
                ('stato_nascita', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato di nascita')),
                ('indirizzo_residenza', models.CharField(max_length=512, null=True, verbose_name='Indirizzo di residenza')),
                ('comune_residenza', models.CharField(max_length=64, null=True, verbose_name='Comune di residenza')),
                ('provincia_residenza', models.CharField(max_length=2, null=True, verbose_name='Provincia di residenza')),
                ('stato_residenza', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato di residenza')),
                ('cap_residenza', models.CharField(max_length=16, null=True, verbose_name='CAP di Residenza')),
                ('email_contatto', models.EmailField(max_length=64, blank=True, verbose_name='Email di contatto')),
                ('avatar', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), blank=True, null=True, validators=[anagrafica.validators.valida_dimensione_file_5mb], verbose_name='Avatar')),
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
                'verbose_name_plural': 'Politiche di Privacy',
                'verbose_name': 'Politica di Privacy',
            },
        ),
        migrations.CreateModel(
            name='ProvvedimentoDisciplinare',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=64, db_index=True)),
                ('vecchio_id', models.IntegerField(default=None, blank=True, null=True, db_index=True)),
                ('estensione', models.CharField(max_length=1, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], db_index=True, verbose_name='Estensione')),
                ('tipo', models.CharField(max_length=1, default='C', choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], db_index=True, verbose_name='Tipologia')),
                ('telefono', models.CharField(max_length=64, blank=True, verbose_name='Telefono')),
                ('fax', models.CharField(max_length=64, blank=True, verbose_name='FAX')),
                ('email', models.CharField(max_length=64, blank=True, verbose_name='Indirizzo e-mail')),
                ('codice_fiscale', models.CharField(max_length=32, blank=True, verbose_name='Codice Fiscale')),
                ('partita_iva', models.CharField(max_length=32, blank=True, verbose_name='Partita IVA')),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, populate_from=anagrafica.models.Sede.sorgente_slug, slugify=base.utils.sede_slugify, editable=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(blank=True, related_name='figli', null=True, to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Sedi CRI',
                'verbose_name': 'Sede CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.CharField(max_length=16, verbose_name='Numero di telefono')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('protocollo_numero', models.CharField(max_length=16, blank=True, null=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(blank=True, null=True, verbose_name='Data di presa in carico')),
                ('motivo', models.CharField(max_length=2048, null=True)),
                ('appartenenza', models.ForeignKey(blank=True, related_name='trasferimento', null=True, to='anagrafica.Appartenenza')),
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
                ('provvedimentodisciplinare_ptr', models.OneToOneField(serialize=False, parent_link=True, to='anagrafica.ProvvedimentoDisciplinare', primary_key=True, auto_created=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, blank=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, verbose_name='Fine', db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('anagrafica.provvedimentodisciplinare', models.Model),
        ),
    ]
