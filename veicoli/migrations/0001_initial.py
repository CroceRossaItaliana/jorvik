# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autoparco',
            fields=[
                ('conestensione_ptr', models.OneToOneField(primary_key=True, to='base.ConEstensione', serialize=False, auto_created=True, parent_link=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Autoparchi',
            },
            bases=('base.conestensione', models.Model),
        ),
        migrations.CreateModel(
            name='Collocazione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(blank=True, verbose_name='Fine', db_index=True, default=None, null=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(blank=True, verbose_name='Fine', db_index=True, default=None, null=True)),
            ],
            options={
                'verbose_name': 'Fermo tecnico',
                'verbose_name_plural': 'Fermi tecnici',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'verbose_name': 'Intervento di Manutenzione',
                'verbose_name_plural': 'Interventi di Manutenzione',
            },
        ),
        migrations.CreateModel(
            name='Rifornimento',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.PositiveIntegerField(verbose_name='Num. rifornimento', db_index=True, default=1)),
                ('data', models.DateTimeField(verbose_name='Data rifornimento', db_index=True)),
                ('contachilometri', models.PositiveIntegerField(verbose_name='Contachilometri', db_index=True)),
                ('consumo_carburante', models.FloatField(blank=True, verbose_name='Consumo carburante lt.', db_index=True, default=None, null=True)),
                ('consumo_olio_m', models.FloatField(blank=True, verbose_name='Consumo Olio motori Kg.', db_index=True, default=None, null=True)),
                ('consumo_olio_t', models.FloatField(blank=True, verbose_name='Consumo Olio trasmissioni Kg.', db_index=True, default=None, null=True)),
                ('consumo_olio_i', models.FloatField(blank=True, verbose_name='Consumo Olio idraulico Kg.', db_index=True, default=None, null=True)),
                ('presso', models.CharField(choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], verbose_name='Presso', max_length=1, default='D')),
                ('contalitri', models.FloatField(blank=True, verbose_name='(c/o Cisterna int.) Contalitri', db_index=True, default=None, null=True)),
                ('ricevuta', models.CharField(max_length=32, db_index=True, null=True, blank=True, verbose_name='(c/o Distributore) N. Ricevuta', default=None)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('descrizione', models.TextField(verbose_name='Descrizione', max_length=1024)),
                ('autore', models.ForeignKey(related_name='segnalazioni', to='anagrafica.Persona')),
                ('manutenzione', models.ForeignKey(related_name='segnalazioni', to='veicoli.Manutenzione', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], verbose_name='Stato', max_length=2, default='OK')),
                ('libretto', models.CharField(verbose_name='N. Libretto', max_length=16, db_index=True, help_text='Formato 201X-XXXXXXXXX')),
                ('targa', models.CharField(verbose_name='Targa (A)', max_length=5, db_index=True, help_text='Targa del Veicolo, senza spazi.')),
                ('formato_targa', models.CharField(choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], verbose_name='Formato Targa', max_length=1, default='A')),
                ('prima_immatricolazione', models.DateField(verbose_name='Prima Immatricolazione (B)', db_index=True)),
                ('proprietario_cognome', models.CharField(verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', max_length=127, default='Croce Rossa Italiana')),
                ('proprietario_nome', models.CharField(verbose_name='Proprietario: Nome o Iniziale (C2.2)', max_length=127, default='Comitato Centrale')),
                ('proprietario_indirizzo', models.CharField(verbose_name='Proprietario: Indirizzo (C2.3)', max_length=127, default='Via Toscana, 12, 00187 Roma (RM), Italia')),
                ('pneumatici_anteriori', models.CharField(verbose_name='Pneumatici: Anteriori', max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_posteriori', models.CharField(verbose_name='Pneumatici: Posteriori', max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_alt_anteriori', models.CharField(blank=True, verbose_name='Pneumatici alternativi: Anteriori', max_length=32, null=True, help_text='es. 215/70 R12C')),
                ('pneumatici_alt_posteriori', models.CharField(blank=True, verbose_name='Pneumatici alternativi: Posteriori', max_length=32, null=True, help_text='es. 215/70 R12C')),
                ('cambio', models.CharField(verbose_name='Cambio', max_length=32, default='Meccanico', help_text='Tipologia di Cambio')),
                ('lunghezza', models.FloatField(blank=True, verbose_name='Lunghezza m.', null=True)),
                ('larghezza', models.FloatField(blank=True, verbose_name='Larghezza m.', null=True)),
                ('sbalzo', models.FloatField(blank=True, verbose_name='Sbalzo m.', null=True)),
                ('tara', models.PositiveIntegerField(blank=True, verbose_name='Tara kg.', null=True)),
                ('marca', models.CharField(verbose_name='Marca (D.1)', max_length=32, help_text='es. Fiat')),
                ('modello', models.CharField(verbose_name='Tipo (D.2)', max_length=32, help_text='es. Ducato')),
                ('telaio', models.CharField(unique=True, verbose_name='Numero Identificazione Veicolo (E)', max_length=24, db_index=True, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX')),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(verbose_name='Data immatricolazione attuale (I)', db_index=True)),
                ('categoria', models.CharField(verbose_name='Categoria del Veicolo (J)', max_length=16, db_index=True, help_text='es. Ambulanza')),
                ('destinazione', models.CharField(verbose_name='Destinazione ed uso (J.1)', max_length=32, help_text='es. Amb. Soccorso (AMB-A)')),
                ('carrozzeria', models.CharField(verbose_name='Carrozzeria (J.2)', max_length=16, help_text='es. Chiuso')),
                ('omologazione', models.CharField(blank=True, verbose_name='N. Omologazione (K)', max_length=32, null=True, help_text='es. OEXXXXXXXXXX')),
                ('num_assi', models.PositiveSmallIntegerField(verbose_name='Num. Assi (L)', default=2)),
                ('rimorchio_frenato', models.FloatField(blank=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', null=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], verbose_name='Alimentazione (P.3)', max_length=1, default='B')),
                ('posti', models.SmallIntegerField(verbose_name='N. Posti a sedere conducente compreso (S.1)', default=5)),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(blank=True, verbose_name='N. Card Rifornimento', max_length=64, null=True)),
                ('selettiva_radio', models.CharField(blank=True, verbose_name='Selettiva Radio', max_length=64, null=True)),
                ('telepass', models.CharField(blank=True, verbose_name='Numero Telepass', max_length=64, null=True)),
                ('intervallo_revisione', models.PositiveIntegerField(choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], verbose_name='Intervallo Revisione', default=365)),
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
            field=models.ForeignKey(to='veicoli.Segnalazione', null=True, blank=True, default=None, help_text='Rapporto conducente'),
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
