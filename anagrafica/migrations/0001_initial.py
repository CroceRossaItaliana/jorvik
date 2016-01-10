# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.utils
import mptt.fields
import base.stringhe
import anagrafica.validators
import autoslug.fields
import anagrafica.models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, db_index=True, blank=True, default=None, verbose_name='Fine')),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('membro', models.CharField(max_length=2, choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], default='VO', verbose_name='Tipo membro', db_index=True)),
                ('terminazione', models.CharField(max_length=1, null=True, db_index=True, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], blank=True, default=None, verbose_name='Terminazione')),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, db_index=True, blank=True, default=None, verbose_name='Fine')),
                ('tipo', models.CharField(choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2, db_index=True)),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('tipo', models.CharField(max_length=1, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], default='I', db_index=True)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='File')),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='Fototessera')),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('vecchio_id', models.IntegerField(blank=True, default=None, null=True, db_index=True)),
                ('nome', models.CharField(max_length=64, verbose_name='Nome')),
                ('cognome', models.CharField(max_length=64, verbose_name='Cognome')),
                ('codice_fiscale', models.CharField(max_length=16, verbose_name='Codice Fiscale', validators=[anagrafica.validators.valida_codice_fiscale], unique=True, db_index=True)),
                ('data_nascita', models.DateField(verbose_name='Data di nascita', null=True, db_index=True)),
                ('genere', models.CharField(choices=[('M', 'Maschio'), ('F', 'Femmina')], max_length=1, verbose_name='Genere', db_index=True)),
                ('stato', models.CharField(max_length=1, choices=[('P', 'Persona')], default='P', verbose_name='Stato', db_index=True)),
                ('comune_nascita', models.CharField(max_length=64, blank=True, verbose_name='Comune di Nascita')),
                ('provincia_nascita', models.CharField(max_length=2, blank=True, verbose_name='Provincia di Nascita')),
                ('stato_nascita', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato di nascita')),
                ('indirizzo_residenza', models.CharField(max_length=512, null=True, verbose_name='Indirizzo di residenza')),
                ('comune_residenza', models.CharField(max_length=64, null=True, verbose_name='Comune di residenza')),
                ('provincia_residenza', models.CharField(max_length=2, null=True, verbose_name='Provincia di residenza')),
                ('stato_residenza', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato di residenza')),
                ('cap_residenza', models.CharField(max_length=16, null=True, verbose_name='CAP di Residenza')),
                ('email_contatto', models.EmailField(max_length=64, blank=True, verbose_name='Email di contatto')),
                ('avatar', models.ImageField(null=True, upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), validators=[anagrafica.validators.valida_dimensione_file_5mb], blank=True, verbose_name='Avatar')),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('campo', models.CharField(choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')], max_length=8, db_index=True)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(max_length=64, db_index=True)),
                ('vecchio_id', models.IntegerField(blank=True, default=None, null=True, db_index=True)),
                ('estensione', models.CharField(choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], max_length=1, verbose_name='Estensione', db_index=True)),
                ('tipo', models.CharField(max_length=1, choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], default='C', verbose_name='Tipologia', db_index=True)),
                ('telefono', models.CharField(max_length=64, blank=True, verbose_name='Telefono')),
                ('fax', models.CharField(max_length=64, blank=True, verbose_name='FAX')),
                ('email', models.CharField(max_length=64, blank=True, verbose_name='Indirizzo e-mail')),
                ('codice_fiscale', models.CharField(max_length=32, blank=True, verbose_name='Codice Fiscale')),
                ('partita_iva', models.CharField(max_length=32, blank=True, verbose_name='Partita IVA')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=anagrafica.models.Sede.sorgente_slug, always_update=True, slugify=base.utils.sede_slugify)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('genitore', mptt.fields.TreeForeignKey(to='anagrafica.Sede', related_name='figli', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Sede CRI',
                'verbose_name_plural': 'Sedi CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.CharField(max_length=16, verbose_name='Numero di telefono')),
                ('servizio', models.BooleanField(default=False, verbose_name='Numero di servizio')),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('protocollo_numero', models.CharField(max_length=16, blank=True, null=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(blank=True, null=True, verbose_name='Data di presa in carico')),
                ('motivo', models.CharField(max_length=2048, null=True)),
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
                ('provvedimentodisciplinare_ptr', models.OneToOneField(to='anagrafica.ProvvedimentoDisciplinare', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
                ('inizio', models.DateTimeField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', null=True, db_index=True, blank=True, default=None, verbose_name='Fine')),
            ],
            options={
                'abstract': False,
            },
            bases=('anagrafica.provvedimentodisciplinare', models.Model),
        ),
    ]
