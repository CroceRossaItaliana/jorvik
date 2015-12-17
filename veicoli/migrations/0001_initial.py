# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autoparco',
            fields=[
                ('conestensione_ptr', models.OneToOneField(parent_link=True, serialize=False, to='base.ConEstensione', primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(default=None, blank=True, verbose_name='Fine', db_index=True, null=True)),
                ('autoparco', models.ForeignKey(to='veicoli.Autoparco', related_name='autoparco')),
            ],
            options={
                'verbose_name_plural': 'Collocazioni veicolo',
                'verbose_name': 'Collocazione veicolo',
            },
        ),
        migrations.CreateModel(
            name='FermoTecnico',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(default=None, blank=True, verbose_name='Fine', db_index=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Fermi tecnici',
                'verbose_name': 'Fermo tecnico',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('richiedente', models.ForeignKey(to='anagrafica.Sede', related_name='immatricolazioni_richieste')),
                ('ufficio', models.ForeignKey(to='anagrafica.Sede', related_name='immatricolazioni_istruite')),
            ],
            options={
                'verbose_name_plural': 'Pratiche di Immatricolazione',
                'verbose_name': 'Pratica di Immatricolazione',
            },
        ),
        migrations.CreateModel(
            name='Manutenzione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.PositiveIntegerField(default=1, db_index=True, verbose_name='Num. rifornimento')),
                ('data', models.DateTimeField(db_index=True, verbose_name='Data rifornimento')),
                ('contachilometri', models.PositiveIntegerField(db_index=True, verbose_name='Contachilometri')),
                ('consumo_carburante', models.FloatField(default=None, blank=True, verbose_name='Consumo carburante lt.', db_index=True, null=True)),
                ('consumo_olio_m', models.FloatField(default=None, blank=True, verbose_name='Consumo Olio motori Kg.', db_index=True, null=True)),
                ('consumo_olio_t', models.FloatField(default=None, blank=True, verbose_name='Consumo Olio trasmissioni Kg.', db_index=True, null=True)),
                ('consumo_olio_i', models.FloatField(default=None, blank=True, verbose_name='Consumo Olio idraulico Kg.', db_index=True, null=True)),
                ('presso', models.CharField(default='D', max_length=1, choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], verbose_name='Presso')),
                ('contalitri', models.FloatField(default=None, blank=True, verbose_name='(c/o Cisterna int.) Contalitri', db_index=True, null=True)),
                ('ricevuta', models.CharField(default=None, db_index=True, max_length=32, verbose_name='(c/o Distributore) N. Ricevuta', blank=True, null=True)),
                ('conducente', models.ForeignKey(to='anagrafica.Persona', related_name='rifornimenti')),
            ],
            options={
                'verbose_name_plural': 'Rifornimenti di carburante',
                'verbose_name': 'Rifornimento di carburante',
            },
        ),
        migrations.CreateModel(
            name='Segnalazione',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('descrizione', models.TextField(max_length=1024, verbose_name='Descrizione')),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='segnalazioni')),
                ('manutenzione', models.ForeignKey(related_name='segnalazioni', blank=True, to='veicoli.Manutenzione', null=True)),
            ],
            options={
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(default='OK', max_length=2, choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], verbose_name='Stato')),
                ('libretto', models.CharField(max_length=16, help_text='Formato 201X-XXXXXXXXX', db_index=True, verbose_name='N. Libretto')),
                ('targa', models.CharField(max_length=5, help_text='Targa del Veicolo, senza spazi.', db_index=True, verbose_name='Targa (A)')),
                ('formato_targa', models.CharField(default='A', max_length=1, choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], verbose_name='Formato Targa')),
                ('prima_immatricolazione', models.DateField(db_index=True, verbose_name='Prima Immatricolazione (B)')),
                ('proprietario_cognome', models.CharField(default='Croce Rossa Italiana', max_length=127, verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)')),
                ('proprietario_nome', models.CharField(default='Comitato Centrale', max_length=127, verbose_name='Proprietario: Nome o Iniziale (C2.2)')),
                ('proprietario_indirizzo', models.CharField(default='Via Toscana, 12, 00187 Roma (RM), Italia', max_length=127, verbose_name='Proprietario: Indirizzo (C2.3)')),
                ('pneumatici_anteriori', models.CharField(help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici: Anteriori')),
                ('pneumatici_posteriori', models.CharField(help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici: Posteriori')),
                ('pneumatici_alt_anteriori', models.CharField(help_text='es. 215/70 R12C', verbose_name='Pneumatici alternativi: Anteriori', max_length=32, blank=True, null=True)),
                ('pneumatici_alt_posteriori', models.CharField(help_text='es. 215/70 R12C', verbose_name='Pneumatici alternativi: Posteriori', max_length=32, blank=True, null=True)),
                ('cambio', models.CharField(default='Meccanico', help_text='Tipologia di Cambio', max_length=32, verbose_name='Cambio')),
                ('lunghezza', models.FloatField(blank=True, verbose_name='Lunghezza m.', null=True)),
                ('larghezza', models.FloatField(blank=True, verbose_name='Larghezza m.', null=True)),
                ('sbalzo', models.FloatField(blank=True, verbose_name='Sbalzo m.', null=True)),
                ('tara', models.PositiveIntegerField(blank=True, verbose_name='Tara kg.', null=True)),
                ('marca', models.CharField(help_text='es. Fiat', max_length=32, verbose_name='Marca (D.1)')),
                ('modello', models.CharField(help_text='es. Ducato', max_length=32, verbose_name='Tipo (D.2)')),
                ('telaio', models.CharField(max_length=24, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', unique=True, db_index=True, verbose_name='Numero Identificazione Veicolo (E)')),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(db_index=True, verbose_name='Data immatricolazione attuale (I)')),
                ('categoria', models.CharField(max_length=16, help_text='es. Ambulanza', db_index=True, verbose_name='Categoria del Veicolo (J)')),
                ('destinazione', models.CharField(help_text='es. Amb. Soccorso (AMB-A)', max_length=32, verbose_name='Destinazione ed uso (J.1)')),
                ('carrozzeria', models.CharField(help_text='es. Chiuso', max_length=16, verbose_name='Carrozzeria (J.2)')),
                ('omologazione', models.CharField(help_text='es. OEXXXXXXXXXX', verbose_name='N. Omologazione (K)', max_length=32, blank=True, null=True)),
                ('num_assi', models.PositiveSmallIntegerField(default=2, verbose_name='Num. Assi (L)')),
                ('rimorchio_frenato', models.FloatField(blank=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', null=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(default='B', max_length=1, choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], verbose_name='Alimentazione (P.3)')),
                ('posti', models.SmallIntegerField(default=5, verbose_name='N. Posti a sedere conducente compreso (S.1)')),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(max_length=64, verbose_name='N. Card Rifornimento', blank=True, null=True)),
                ('selettiva_radio', models.CharField(max_length=64, verbose_name='Selettiva Radio', blank=True, null=True)),
                ('telepass', models.CharField(max_length=64, verbose_name='Numero Telepass', blank=True, null=True)),
                ('intervallo_revisione', models.PositiveIntegerField(default=365, choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], verbose_name='Intervallo Revisione')),
            ],
            options={
                'verbose_name_plural': 'Veicoli',
            },
        ),
        migrations.AddField(
            model_name='segnalazione',
            name='veicolo',
            field=models.ForeignKey(to='veicoli.Veicolo', related_name='segnalazioni'),
        ),
        migrations.AddField(
            model_name='rifornimento',
            name='segnalazione',
            field=models.ForeignKey(default=None, to='veicoli.Segnalazione', help_text='Rapporto conducente', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rifornimento',
            name='veicolo',
            field=models.ForeignKey(to='veicoli.Veicolo', related_name='rifornimenti'),
        ),
        migrations.AddField(
            model_name='immatricolazione',
            name='veicolo',
            field=models.ForeignKey(to='veicoli.Veicolo', related_name='richieste_immatricolazione'),
        ),
        migrations.AddField(
            model_name='fermotecnico',
            name='veicolo',
            field=models.ForeignKey(to='veicoli.Veicolo', related_name='fermi_tecnici'),
        ),
        migrations.AddField(
            model_name='collocazione',
            name='veicolo',
            field=models.ForeignKey(to='veicoli.Veicolo', related_name='collocazioni'),
        ),
    ]
