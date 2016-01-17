# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.stringhe
import anagrafica.models
import autoslug.fields
import base.utils
import anagrafica.validators
import django_countries.fields
import mptt.fields
import base.tratti


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('membro', models.CharField(max_length=2, db_index=True, default='VO', choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], verbose_name='Tipo membro')),
                ('terminazione', models.CharField(db_index=True, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], verbose_name='Terminazione', blank=True, default=None, max_length=1, null=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Delega',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('tipo', models.CharField(max_length=2, db_index=True, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('GR', 'Referente Gruppo'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('DC', 'Direttore Corso'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')])),
                ('oggetto_id', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Deleghe',
            },
        ),
        migrations.CreateModel(
            name='Dimissione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('motivo', models.CharField(max_length=2, choices=[('VOL', 'Dimissioni Volontarie'), ('TUR', 'Mancato svolgimento turno'), ('RIS', 'Mancato rientro da riserva'), ('QUO', 'Mancato versamento quota annuale'), ('RAD', 'Radiazione da Croce Rossa Italiana'), ('DEC', 'Decesso')])),
                ('info', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name_plural': 'Documenti di Dimissione',
                'verbose_name': 'Documento di Dimissione',
            },
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(max_length=1, db_index=True, default='I', choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale'), ('A', 'Altro')])),
                ('file', models.FileField(validators=[anagrafica.validators.valida_dimensione_file_8mb], upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), verbose_name='File')),
            ],
            options={
                'verbose_name_plural': 'Documenti',
            },
        ),
        migrations.CreateModel(
            name='Estensione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('protocollo_numero', models.CharField(blank=True, max_length=512, verbose_name='Numero di protocollo', null=True)),
                ('protocollo_data', models.DateField(blank=True, verbose_name='Data di presa in carico', null=True)),
                ('motivo', models.CharField(max_length=4096, null=True)),
            ],
            options={
                'verbose_name_plural': 'Richieste di estensione',
                'verbose_name': 'Richiesta di estensione',
            },
            bases=(models.Model, base.tratti.ConPDF),
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('file', models.ImageField(validators=[anagrafica.validators.valida_dimensione_file_8mb], upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), verbose_name='Fototessera')),
            ],
            options={
                'verbose_name_plural': 'Fototessere',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('vecchio_id', models.IntegerField(db_index=True, default=None, blank=True, null=True)),
                ('nome', models.CharField(max_length=64, verbose_name='Nome')),
                ('cognome', models.CharField(max_length=64, verbose_name='Cognome')),
                ('codice_fiscale', base.utils.UpperCaseCharField(unique=True, db_index=True, max_length=16, validators=[anagrafica.validators.valida_codice_fiscale], verbose_name='Codice Fiscale')),
                ('data_nascita', models.DateField(db_index=True, validators=[anagrafica.validators.valida_almeno_14_anni], verbose_name='Data di nascita', null=True)),
                ('genere', models.CharField(max_length=1, db_index=True, choices=[('M', 'Maschio'), ('F', 'Femmina')], verbose_name='Genere')),
                ('stato', models.CharField(max_length=1, db_index=True, default='P', choices=[('P', 'Persona')], verbose_name='Stato')),
                ('comune_nascita', models.CharField(blank=True, max_length=64, verbose_name='Comune di Nascita')),
                ('provincia_nascita', models.CharField(blank=True, max_length=2, verbose_name='Provincia di Nascita')),
                ('stato_nascita', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato di nascita')),
                ('indirizzo_residenza', models.CharField(max_length=512, verbose_name='Indirizzo di residenza', null=True)),
                ('comune_residenza', models.CharField(max_length=64, verbose_name='Comune di residenza', null=True)),
                ('provincia_residenza', models.CharField(max_length=2, verbose_name='Provincia di residenza', null=True)),
                ('stato_residenza', django_countries.fields.CountryField(max_length=2, default='IT', verbose_name='Stato di residenza')),
                ('cap_residenza', models.CharField(max_length=16, verbose_name='CAP di Residenza', null=True)),
                ('email_contatto', models.EmailField(blank=True, max_length=64, verbose_name='Email di contatto')),
                ('note', models.TextField(blank=True, max_length=10000, verbose_name='Note aggiuntive', null=True)),
                ('avatar', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), verbose_name='Avatar', validators=[anagrafica.validators.valida_dimensione_file_5mb], blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Persone',
            },
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('campo', models.CharField(max_length=8, db_index=True, choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')])),
                ('policy', models.PositiveSmallIntegerField(db_index=True, choices=[(8, 'Pubblico'), (6, 'Utenti di Gaia'), (4, 'A tutti i membri della mia Sede CRI'), (2, 'Ai Responsabili della mia Sede CRI'), (0, 'Solo a me')])),
            ],
            options={
                'verbose_name_plural': 'Politiche di Privacy',
                'verbose_name': 'Politica di Privacy',
            },
        ),
        migrations.CreateModel(
            name='ProvvedimentoDisciplinare',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('protocollo_data', models.DateField(db_index=True)),
                ('protocollo_numero', models.IntegerField()),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('motivazione', models.CharField(max_length=500)),
                ('tipo', models.CharField(max_length=1, default='A', choices=[('A', 'Ammonizione'), ('S', 'Sospensione'), ('E', 'Esplusione')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Riserva',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, base.tratti.ConPDF),
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, max_length=64)),
                ('vecchio_id', models.IntegerField(db_index=True, default=None, blank=True, null=True)),
                ('estensione', models.CharField(max_length=1, db_index=True, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione')),
                ('tipo', models.CharField(max_length=1, db_index=True, default='C', choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], verbose_name='Tipologia')),
                ('telefono', models.CharField(blank=True, max_length=64, verbose_name='Telefono')),
                ('fax', models.CharField(blank=True, max_length=64, verbose_name='FAX')),
                ('email', models.CharField(blank=True, max_length=64, verbose_name='Indirizzo e-mail')),
                ('codice_fiscale', models.CharField(blank=True, max_length=32, verbose_name='Codice Fiscale')),
                ('partita_iva', models.CharField(blank=True, max_length=32, verbose_name='Partita IVA')),
                ('attiva', models.BooleanField(db_index=True, default=True, verbose_name='Attiva')),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, slugify=base.utils.sede_slugify, populate_from=anagrafica.models.Sede.sorgente_slug, editable=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(related_name='figli', blank=True, to='anagrafica.Sede', null=True)),
            ],
            options={
                'verbose_name_plural': 'Sedi CRI',
                'verbose_name': 'Sede CRI',
            },
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('protocollo_numero', models.CharField(blank=True, max_length=16, verbose_name='Numero di protocollo', null=True)),
                ('protocollo_data', models.DateField(blank=True, verbose_name='Data di presa in carico', null=True)),
                ('motivo', models.CharField(max_length=2048, null=True)),
                ('appartenenza', models.ForeignKey(related_name='trasferimento', blank=True, to='anagrafica.Appartenenza', null=True)),
                ('destinazione', models.ForeignKey(related_name='trasferimenti_destinazione', to='anagrafica.Sede')),
                ('persona', models.ForeignKey(related_name='trasferimenti', to='anagrafica.Persona')),
                ('richiedente', models.ForeignKey(related_name='trasferimenti_richiesti_da', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Richieste di trasferimento',
                'verbose_name': 'Richiesta di trasferimento',
            },
            bases=(models.Model, base.tratti.ConPDF),
        ),
    ]
