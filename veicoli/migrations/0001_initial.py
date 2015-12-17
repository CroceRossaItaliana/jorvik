# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autoparco',
            fields=[
                ('conestensione_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='base.ConEstensione')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Autoparchi',
            },
            bases=('base.conestensione', models.Model),
        ),
        migrations.CreateModel(
            name='Collocazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(null=True, verbose_name='Fine', default=None, blank=True, db_index=True)),
                ('autoparco', models.ForeignKey(related_name='autoparco', to='veicoli.Autoparco')),
            ],
            options={
                'verbose_name': 'Collocazione veicolo',
                'verbose_name_plural': 'Collocazioni veicolo',
            },
        ),
        migrations.CreateModel(
            name='FermoTecnico',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(null=True, verbose_name='Fine', default=None, blank=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Fermo tecnico',
                'verbose_name_plural': 'Fermi tecnici',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('richiedente', models.ForeignKey(related_name='immatricolazioni_richieste', to='anagrafica.Sede')),
                ('ufficio', models.ForeignKey(related_name='immatricolazioni_istruite', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name': 'Pratica di Immatricolazione',
                'verbose_name_plural': 'Pratiche di Immatricolazione',
            },
        ),
        migrations.CreateModel(
            name='Manutenzione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Intervento di Manutenzione',
                'verbose_name_plural': 'Interventi di Manutenzione',
            },
        ),
        migrations.CreateModel(
            name='Rifornimento',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.PositiveIntegerField(verbose_name='Num. rifornimento', default=1, db_index=True)),
                ('data', models.DateTimeField(verbose_name='Data rifornimento', db_index=True)),
                ('contachilometri', models.PositiveIntegerField(verbose_name='Contachilometri', db_index=True)),
                ('consumo_carburante', models.FloatField(null=True, verbose_name='Consumo carburante lt.', default=None, blank=True, db_index=True)),
                ('consumo_olio_m', models.FloatField(null=True, verbose_name='Consumo Olio motori Kg.', default=None, blank=True, db_index=True)),
                ('consumo_olio_t', models.FloatField(null=True, verbose_name='Consumo Olio trasmissioni Kg.', default=None, blank=True, db_index=True)),
                ('consumo_olio_i', models.FloatField(null=True, verbose_name='Consumo Olio idraulico Kg.', default=None, blank=True, db_index=True)),
                ('presso', models.CharField(max_length=1, verbose_name='Presso', default='D', choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')])),
                ('contalitri', models.FloatField(null=True, verbose_name='(c/o Cisterna int.) Contalitri', default=None, blank=True, db_index=True)),
                ('ricevuta', models.CharField(null=True, default=None, db_index=True, max_length=32, verbose_name='(c/o Distributore) N. Ricevuta', blank=True)),
                ('conducente', models.ForeignKey(related_name='rifornimenti', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Rifornimento di carburante',
                'verbose_name_plural': 'Rifornimenti di carburante',
            },
        ),
        migrations.CreateModel(
            name='Segnalazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('descrizione', models.TextField(max_length=1024, verbose_name='Descrizione')),
                ('autore', models.ForeignKey(related_name='segnalazioni', to='anagrafica.Persona')),
                ('manutenzione', models.ForeignKey(null=True, blank=True, related_name='segnalazioni', to='veicoli.Manutenzione')),
            ],
            options={
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(max_length=2, verbose_name='Stato', default='OK', choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')])),
                ('libretto', models.CharField(help_text='Formato 201X-XXXXXXXXX', max_length=16, verbose_name='N. Libretto', db_index=True)),
                ('targa', models.CharField(help_text='Targa del Veicolo, senza spazi.', max_length=5, verbose_name='Targa (A)', db_index=True)),
                ('formato_targa', models.CharField(max_length=1, verbose_name='Formato Targa', default='A', choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')])),
                ('prima_immatricolazione', models.DateField(verbose_name='Prima Immatricolazione (B)', db_index=True)),
                ('proprietario_cognome', models.CharField(max_length=127, verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', default='Croce Rossa Italiana')),
                ('proprietario_nome', models.CharField(max_length=127, verbose_name='Proprietario: Nome o Iniziale (C2.2)', default='Comitato Centrale')),
                ('proprietario_indirizzo', models.CharField(max_length=127, verbose_name='Proprietario: Indirizzo (C2.3)', default='Via Toscana, 12, 00187 Roma (RM), Italia')),
                ('pneumatici_anteriori', models.CharField(help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici: Anteriori')),
                ('pneumatici_posteriori', models.CharField(help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici: Posteriori')),
                ('pneumatici_alt_anteriori', models.CharField(help_text='es. 215/70 R12C', null=True, verbose_name='Pneumatici alternativi: Anteriori', blank=True, max_length=32)),
                ('pneumatici_alt_posteriori', models.CharField(help_text='es. 215/70 R12C', null=True, verbose_name='Pneumatici alternativi: Posteriori', blank=True, max_length=32)),
                ('cambio', models.CharField(help_text='Tipologia di Cambio', max_length=32, verbose_name='Cambio', default='Meccanico')),
                ('lunghezza', models.FloatField(null=True, verbose_name='Lunghezza m.', blank=True)),
                ('larghezza', models.FloatField(null=True, verbose_name='Larghezza m.', blank=True)),
                ('sbalzo', models.FloatField(null=True, verbose_name='Sbalzo m.', blank=True)),
                ('tara', models.PositiveIntegerField(null=True, verbose_name='Tara kg.', blank=True)),
                ('marca', models.CharField(help_text='es. Fiat', max_length=32, verbose_name='Marca (D.1)')),
                ('modello', models.CharField(help_text='es. Ducato', max_length=32, verbose_name='Tipo (D.2)')),
                ('telaio', models.CharField(help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', max_length=24, verbose_name='Numero Identificazione Veicolo (E)', unique=True, db_index=True)),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(verbose_name='Data immatricolazione attuale (I)', db_index=True)),
                ('categoria', models.CharField(help_text='es. Ambulanza', max_length=16, verbose_name='Categoria del Veicolo (J)', db_index=True)),
                ('destinazione', models.CharField(help_text='es. Amb. Soccorso (AMB-A)', max_length=32, verbose_name='Destinazione ed uso (J.1)')),
                ('carrozzeria', models.CharField(help_text='es. Chiuso', max_length=16, verbose_name='Carrozzeria (J.2)')),
                ('omologazione', models.CharField(help_text='es. OEXXXXXXXXXX', null=True, verbose_name='N. Omologazione (K)', blank=True, max_length=32)),
                ('num_assi', models.PositiveSmallIntegerField(verbose_name='Num. Assi (L)', default=2)),
                ('rimorchio_frenato', models.FloatField(null=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', blank=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(max_length=1, verbose_name='Alimentazione (P.3)', default='B', choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')])),
                ('posti', models.SmallIntegerField(verbose_name='N. Posti a sedere conducente compreso (S.1)', default=5)),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(null=True, max_length=64, verbose_name='N. Card Rifornimento', blank=True)),
                ('selettiva_radio', models.CharField(null=True, max_length=64, verbose_name='Selettiva Radio', blank=True)),
                ('telepass', models.CharField(null=True, max_length=64, verbose_name='Numero Telepass', blank=True)),
                ('intervallo_revisione', models.PositiveIntegerField(verbose_name='Intervallo Revisione', default=365, choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')])),
            ],
            options={
                'verbose_name_plural': 'Veicoli',
            },
        ),
        migrations.AddField(
            model_name='segnalazione',
            name='veicolo',
            field=models.ForeignKey(related_name='segnalazioni', to='veicoli.Veicolo'),
        ),
        migrations.AddField(
            model_name='rifornimento',
            name='segnalazione',
            field=models.ForeignKey(help_text='Rapporto conducente', null=True, default=None, blank=True, to='veicoli.Segnalazione'),
        ),
        migrations.AddField(
            model_name='rifornimento',
            name='veicolo',
            field=models.ForeignKey(related_name='rifornimenti', to='veicoli.Veicolo'),
        ),
        migrations.AddField(
            model_name='immatricolazione',
            name='veicolo',
            field=models.ForeignKey(related_name='richieste_immatricolazione', to='veicoli.Veicolo'),
        ),
        migrations.AddField(
            model_name='fermotecnico',
            name='veicolo',
            field=models.ForeignKey(related_name='fermi_tecnici', to='veicoli.Veicolo'),
        ),
        migrations.AddField(
            model_name='collocazione',
            name='veicolo',
            field=models.ForeignKey(related_name='collocazioni', to='veicoli.Veicolo'),
        ),
    ]
