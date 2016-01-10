# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields
import base.utils
import base.stringhe
import autoslug.fields
import anagrafica.validators
import mptt.fields
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
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, null=True, db_index=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', verbose_name='Fine', blank=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('membro', models.CharField(db_index=True, default='VO', choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], verbose_name='Tipo membro', max_length=2)),
                ('terminazione', models.CharField(default=None, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], max_length=1, null=True, db_index=True, verbose_name='Terminazione', blank=True)),
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
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, null=True, db_index=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', verbose_name='Fine', blank=True)),
                ('tipo', models.CharField(db_index=True, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
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
                ('tipo', models.CharField(db_index=True, default='I', choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], max_length=1)),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='File')),
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
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('protocollo_numero', models.PositiveIntegerField(blank=True, null=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(blank=True, null=True, verbose_name='Data di presa in carico')),
                ('attuale', models.CharField(default='s', verbose_name='Attualità della richiesta', max_length=1)),
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
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), validators=[anagrafica.validators.valida_dimensione_file_8mb], verbose_name='Fototessera')),
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
                ('vecchio_id', models.IntegerField(db_index=True, default=None, blank=True, null=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=64)),
                ('cognome', models.CharField(verbose_name='Cognome', max_length=64)),
                ('codice_fiscale', models.CharField(unique=True, db_index=True, max_length=16, validators=[anagrafica.validators.valida_codice_fiscale], verbose_name='Codice Fiscale')),
                ('data_nascita', models.DateField(db_index=True, verbose_name='Data di nascita', null=True)),
                ('genere', models.CharField(db_index=True, choices=[('M', 'Maschio'), ('F', 'Femmina')], verbose_name='Genere', max_length=1)),
                ('stato', models.CharField(db_index=True, default='P', choices=[('P', 'Persona')], verbose_name='Stato', max_length=1)),
                ('comune_nascita', models.CharField(max_length=64, blank=True, verbose_name='Comune di Nascita')),
                ('provincia_nascita', models.CharField(max_length=2, blank=True, verbose_name='Provincia di Nascita')),
                ('stato_nascita', django_countries.fields.CountryField(default='IT', verbose_name='Stato di nascita', max_length=2)),
                ('indirizzo_residenza', models.CharField(max_length=512, null=True, verbose_name='Indirizzo di residenza')),
                ('comune_residenza', models.CharField(max_length=64, null=True, verbose_name='Comune di residenza')),
                ('provincia_residenza', models.CharField(max_length=2, null=True, verbose_name='Provincia di residenza')),
                ('stato_residenza', django_countries.fields.CountryField(default='IT', verbose_name='Stato di residenza', max_length=2)),
                ('cap_residenza', models.CharField(max_length=16, null=True, verbose_name='CAP di Residenza')),
                ('email_contatto', models.EmailField(max_length=64, blank=True, verbose_name='Email di contatto')),
                ('avatar', models.ImageField(validators=[anagrafica.validators.valida_dimensione_file_5mb], null=True, upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), verbose_name='Avatar', blank=True)),
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
                'verbose_name': 'Politica di Privacy',
                'verbose_name_plural': 'Politiche di Privacy',
            },
        ),
        migrations.CreateModel(
            name='ProvvedimentoDisciplinare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, max_length=64)),
                ('vecchio_id', models.IntegerField(db_index=True, default=None, blank=True, null=True)),
                ('estensione', models.CharField(db_index=True, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione', max_length=1)),
                ('tipo', models.CharField(db_index=True, default='C', choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], verbose_name='Tipologia', max_length=1)),
                ('telefono', models.CharField(max_length=64, blank=True, verbose_name='Telefono')),
                ('fax', models.CharField(max_length=64, blank=True, verbose_name='FAX')),
                ('email', models.CharField(max_length=64, blank=True, verbose_name='Indirizzo e-mail')),
                ('codice_fiscale', models.CharField(max_length=32, blank=True, verbose_name='Codice Fiscale')),
                ('partita_iva', models.CharField(max_length=32, blank=True, verbose_name='Partita IVA')),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from=anagrafica.models.Sede.sorgente_slug, slugify=base.utils.sede_slugify)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(to='anagrafica.Sede', related_name='figli', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Sede CRI',
                'verbose_name_plural': 'Sedi CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.CharField(verbose_name='Numero di telefono', max_length=16)),
                ('servizio', models.BooleanField(default=False, verbose_name='Numero di servizio')),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('protocollo_numero', models.CharField(max_length=16, blank=True, null=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(blank=True, null=True, verbose_name='Data di presa in carico')),
                ('motivo', models.CharField(max_length=2048, null=True)),
                ('appartenenza', models.ForeignKey(to='anagrafica.Appartenenza', related_name='trasferimento', null=True, blank=True)),
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
                ('provvedimentodisciplinare_ptr', models.OneToOneField(to='anagrafica.ProvvedimentoDisciplinare', parent_link=True, primary_key=True, auto_created=True, serialize=False)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(default=None, null=True, db_index=True, help_text='Lasciare il campo vuoto per impostare fine indeterminata.', verbose_name='Fine', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('anagrafica.provvedimentodisciplinare', models.Model),
        ),
    ]
