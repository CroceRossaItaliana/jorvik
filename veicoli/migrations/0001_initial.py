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
                ('conestensione_ptr', models.OneToOneField(parent_link=True, primary_key=True, auto_created=True, serialize=False, to='base.ConEstensione')),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, verbose_name='Fine', null=True, blank=True, default=None)),
                ('autoparco', models.ForeignKey(related_name='autoparco', to='veicoli.Autoparco')),
            ],
            options={
                'verbose_name_plural': 'Collocazioni veicolo',
                'verbose_name': 'Collocazione veicolo',
            },
        ),
        migrations.CreateModel(
            name='FermoTecnico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, verbose_name='Fine', null=True, blank=True, default=None)),
            ],
            options={
                'verbose_name_plural': 'Fermi tecnici',
                'verbose_name': 'Fermo tecnico',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('richiedente', models.ForeignKey(related_name='immatricolazioni_richieste', to='anagrafica.Sede')),
                ('ufficio', models.ForeignKey(related_name='immatricolazioni_istruite', to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Pratiche di Immatricolazione',
                'verbose_name': 'Pratica di Immatricolazione',
            },
        ),
        migrations.CreateModel(
            name='Manutenzione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Interventi di Manutenzione',
                'verbose_name': 'Intervento di Manutenzione',
            },
        ),
        migrations.CreateModel(
            name='Rifornimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.PositiveIntegerField(db_index=True, verbose_name='Num. rifornimento', default=1)),
                ('data', models.DateTimeField(db_index=True, verbose_name='Data rifornimento')),
                ('contachilometri', models.PositiveIntegerField(db_index=True, verbose_name='Contachilometri')),
                ('consumo_carburante', models.FloatField(db_index=True, verbose_name='Consumo carburante lt.', null=True, blank=True, default=None)),
                ('consumo_olio_m', models.FloatField(db_index=True, verbose_name='Consumo Olio motori Kg.', null=True, blank=True, default=None)),
                ('consumo_olio_t', models.FloatField(db_index=True, verbose_name='Consumo Olio trasmissioni Kg.', null=True, blank=True, default=None)),
                ('consumo_olio_i', models.FloatField(db_index=True, verbose_name='Consumo Olio idraulico Kg.', null=True, blank=True, default=None)),
                ('presso', models.CharField(verbose_name='Presso', choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], max_length=1, default='D')),
                ('contalitri', models.FloatField(db_index=True, verbose_name='(c/o Cisterna int.) Contalitri', null=True, blank=True, default=None)),
                ('ricevuta', models.CharField(verbose_name='(c/o Distributore) N. Ricevuta', max_length=32, default=None, db_index=True, blank=True, null=True)),
                ('conducente', models.ForeignKey(related_name='rifornimenti', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Rifornimenti di carburante',
                'verbose_name': 'Rifornimento di carburante',
            },
        ),
        migrations.CreateModel(
            name='Segnalazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('descrizione', models.TextField(verbose_name='Descrizione', max_length=1024)),
                ('autore', models.ForeignKey(related_name='segnalazioni', to='anagrafica.Persona')),
                ('manutenzione', models.ForeignKey(to='veicoli.Manutenzione', null=True, blank=True, related_name='segnalazioni')),
            ],
            options={
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(verbose_name='Stato', choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], max_length=2, default='OK')),
                ('libretto', models.CharField(db_index=True, verbose_name='N. Libretto', help_text='Formato 201X-XXXXXXXXX', max_length=16)),
                ('targa', models.CharField(db_index=True, verbose_name='Targa (A)', help_text='Targa del Veicolo, senza spazi.', max_length=5)),
                ('formato_targa', models.CharField(verbose_name='Formato Targa', choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], max_length=1, default='A')),
                ('prima_immatricolazione', models.DateField(db_index=True, verbose_name='Prima Immatricolazione (B)')),
                ('proprietario_cognome', models.CharField(verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', max_length=127, default='Croce Rossa Italiana')),
                ('proprietario_nome', models.CharField(verbose_name='Proprietario: Nome o Iniziale (C2.2)', max_length=127, default='Comitato Centrale')),
                ('proprietario_indirizzo', models.CharField(verbose_name='Proprietario: Indirizzo (C2.3)', max_length=127, default='Via Toscana, 12, 00187 Roma (RM), Italia')),
                ('pneumatici_anteriori', models.CharField(verbose_name='Pneumatici: Anteriori', help_text='es. 215/70 R12C', max_length=32)),
                ('pneumatici_posteriori', models.CharField(verbose_name='Pneumatici: Posteriori', help_text='es. 215/70 R12C', max_length=32)),
                ('pneumatici_alt_anteriori', models.CharField(verbose_name='Pneumatici alternativi: Anteriori', help_text='es. 215/70 R12C', null=True, blank=True, max_length=32)),
                ('pneumatici_alt_posteriori', models.CharField(verbose_name='Pneumatici alternativi: Posteriori', help_text='es. 215/70 R12C', null=True, blank=True, max_length=32)),
                ('cambio', models.CharField(verbose_name='Cambio', help_text='Tipologia di Cambio', max_length=32, default='Meccanico')),
                ('lunghezza', models.FloatField(verbose_name='Lunghezza m.', blank=True, null=True)),
                ('larghezza', models.FloatField(verbose_name='Larghezza m.', blank=True, null=True)),
                ('sbalzo', models.FloatField(verbose_name='Sbalzo m.', blank=True, null=True)),
                ('tara', models.PositiveIntegerField(verbose_name='Tara kg.', blank=True, null=True)),
                ('marca', models.CharField(verbose_name='Marca (D.1)', help_text='es. Fiat', max_length=32)),
                ('modello', models.CharField(verbose_name='Tipo (D.2)', help_text='es. Ducato', max_length=32)),
                ('telaio', models.CharField(db_index=True, verbose_name='Numero Identificazione Veicolo (E)', help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', max_length=24, unique=True)),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(db_index=True, verbose_name='Data immatricolazione attuale (I)')),
                ('categoria', models.CharField(db_index=True, verbose_name='Categoria del Veicolo (J)', help_text='es. Ambulanza', max_length=16)),
                ('destinazione', models.CharField(verbose_name='Destinazione ed uso (J.1)', help_text='es. Amb. Soccorso (AMB-A)', max_length=32)),
                ('carrozzeria', models.CharField(verbose_name='Carrozzeria (J.2)', help_text='es. Chiuso', max_length=16)),
                ('omologazione', models.CharField(verbose_name='N. Omologazione (K)', help_text='es. OEXXXXXXXXXX', null=True, blank=True, max_length=32)),
                ('num_assi', models.PositiveSmallIntegerField(verbose_name='Num. Assi (L)', default=2)),
                ('rimorchio_frenato', models.FloatField(verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', blank=True, null=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(verbose_name='Alimentazione (P.3)', choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], max_length=1, default='B')),
                ('posti', models.SmallIntegerField(verbose_name='N. Posti a sedere conducente compreso (S.1)', default=5)),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(verbose_name='N. Card Rifornimento', null=True, blank=True, max_length=64)),
                ('selettiva_radio', models.CharField(verbose_name='Selettiva Radio', null=True, blank=True, max_length=64)),
                ('telepass', models.CharField(verbose_name='Numero Telepass', null=True, blank=True, max_length=64)),
                ('intervallo_revisione', models.PositiveIntegerField(verbose_name='Intervallo Revisione', choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], default=365)),
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
            field=models.ForeignKey(help_text='Rapporto conducente', to='veicoli.Segnalazione', null=True, default=None, blank=True),
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
