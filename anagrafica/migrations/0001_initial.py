# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields
import mptt.fields
import base.stringhe
import autoslug.fields
import anagrafica.models
import base.utils


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
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(null=True, db_index=True, blank=True, verbose_name='Fine', default=None)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('membro', models.CharField(db_index=True, choices=[('VO', 'Volontario'), ('ES', 'Volontario in Estensione'), ('OR', 'Socio Ordinario'), ('SO', 'Sostenitore'), ('DI', 'Dipendente'), ('IN', 'Infermiera Volontaria'), ('MI', 'Membro Militare'), ('DO', 'Donatore Finanziario')], max_length=2, verbose_name='Tipo membro', default='VO')),
                ('terminazione', models.CharField(blank=True, max_length=1, null=True, db_index=True, choices=[('D', 'Dimissione'), ('E', 'Espulsione'), ('S', 'Sospensione'), ('T', 'Trasferimento'), ('P', 'Promozione'), ('F', 'Fine Estensione')], verbose_name='Terminazione', default=None)),
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
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(null=True, db_index=True, blank=True, verbose_name='Fine', default=None)),
                ('tipo', models.CharField(db_index=True, choices=[('PR', 'Presidente'), ('US', 'Ufficio Soci'), ('UT', 'Ufficio Soci Temporaneo'), ('DA', "Delegato d'Area"), ('O1', 'Delegato Obiettivo I (Salute)'), ('O2', 'Delegato Obiettivo II (Sociale)'), ('O3', 'Delegato Obiettivo III (Emergenze)'), ('O4', 'Delegato Obiettivo IV (Principi)'), ('O5', 'Delegato Obiettivo V (Giovani)'), ('O6', 'Delegato Obiettivo VI (Sviluppo)'), ('RA', "Responsabile d'Area"), ('RE', 'Referente Attività'), ('CO', 'Delegato Centrale Operativa'), ('RF', 'Responsabile Formazione'), ('AP', 'Responsabile Autoparco'), ('PA', 'Responsabile Patenti'), ('DO', 'Responsabile Donazioni Sangue')], max_length=2)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(db_index=True, choices=[('I', "Carta d'identità"), ('P', 'Patente Civile'), ('S', 'Patente CRI'), ('C', 'Codice Fiscale')], max_length=1, default='I')),
                ('file', models.FileField(upload_to=base.stringhe.GeneratoreNomeFile('documenti/'), verbose_name='File')),
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
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('protocollo_numero', models.PositiveIntegerField(null=True, blank=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(null=True, blank=True, verbose_name='Data di presa in carico')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Fototessera',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('file', models.ImageField(upload_to=base.stringhe.GeneratoreNomeFile('fototessere/'), verbose_name='Fototessera')),
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
                ('nome', models.CharField(max_length=64, verbose_name='Nome')),
                ('cognome', models.CharField(max_length=64, verbose_name='Cognome')),
                ('codice_fiscale', models.CharField(db_index=True, max_length=16, verbose_name='Codice Fiscale', unique=True)),
                ('data_nascita', models.DateField(null=True, db_index=True, verbose_name='Data di nascita')),
                ('genere', models.CharField(db_index=True, choices=[('M', 'Maschio'), ('F', 'Femmina')], max_length=1, verbose_name='Genere')),
                ('stato', models.CharField(db_index=True, choices=[('P', 'Persona')], max_length=1, verbose_name='Stato', default='P')),
                ('comune_nascita', models.CharField(blank=True, max_length=64, verbose_name='Comune di Nascita')),
                ('provincia_nascita', models.CharField(blank=True, max_length=2, verbose_name='Provincia di Nascita')),
                ('stato_nascita', django_countries.fields.CountryField(max_length=2, verbose_name='Stato di nascita', default='IT')),
                ('indirizzo_residenza', models.CharField(blank=True, max_length=512, verbose_name='Indirizzo di residenza')),
                ('comune_residenza', models.CharField(blank=True, max_length=64, verbose_name='Comune di residenza')),
                ('provincia_residenza', models.CharField(blank=True, max_length=2, verbose_name='Provincia di residenza')),
                ('stato_residenza', django_countries.fields.CountryField(max_length=2, verbose_name='Stato di residenza', default='IT')),
                ('cap_residenza', models.CharField(blank=True, max_length=16, verbose_name='CAP di Residenza')),
                ('email_contatto', models.EmailField(blank=True, max_length=64, verbose_name='Email di contatto')),
                ('avatar', models.ImageField(null=True, blank=True, upload_to=base.stringhe.GeneratoreNomeFile('avatar/'), verbose_name='Avatar')),
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
                ('campo', models.CharField(db_index=True, choices=[('email', 'Indirizzo E-mail'), ('cellulare', 'Numeri di Cellulare')], max_length=8)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(db_index=True, max_length=64)),
                ('estensione', models.CharField(db_index=True, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], max_length=1, verbose_name='Estensione')),
                ('tipo', models.CharField(db_index=True, choices=[('C', 'Comitato'), ('M', 'Sede Militare'), ('A', 'Autoparco')], max_length=1, verbose_name='Tipologia', default='C')),
                ('telefono', models.CharField(blank=True, max_length=64, verbose_name='Telefono')),
                ('fax', models.CharField(blank=True, max_length=64, verbose_name='FAX')),
                ('email', models.CharField(blank=True, max_length=64, verbose_name='Indirizzo e-mail')),
                ('codice_fiscale', models.CharField(blank=True, max_length=32, verbose_name='Codice Fiscale')),
                ('partita_iva', models.CharField(blank=True, max_length=32, verbose_name='Partita IVA')),
                ('slug', autoslug.fields.AutoSlugField(slugify=base.utils.sede_slugify, always_update=True, editable=False, populate_from=anagrafica.models.Sede.sorgente_slug)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('genitore', mptt.fields.TreeForeignKey(blank=True, related_name='figli', to='anagrafica.Sede', null=True)),
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
                ('servizio', models.BooleanField(verbose_name='Numero di servizio', default=False)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, verbose_name='Confermata', default=True)),
                ('ritirata', models.BooleanField(db_index=True, verbose_name='Ritirata', default=False)),
                ('protocollo_numero', models.PositiveIntegerField(null=True, blank=True, verbose_name='Numero di protocollo')),
                ('protocollo_data', models.DateField(null=True, blank=True, verbose_name='Data di presa in carico')),
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
                ('provvedimentodisciplinare_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='anagrafica.ProvvedimentoDisciplinare', serialize=False, auto_created=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(null=True, db_index=True, blank=True, verbose_name='Fine', default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=('anagrafica.provvedimentodisciplinare', models.Model),
        ),
    ]
