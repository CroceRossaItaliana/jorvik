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
                ('conestensione_ptr', models.OneToOneField(serialize=False, auto_created=True, to='base.ConEstensione', primary_key=True, parent_link=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(verbose_name='Fine', blank=True, default=None, null=True, db_index=True)),
                ('autoparco', models.ForeignKey(to='veicoli.Autoparco', related_name='autoparco')),
            ],
            options={
                'verbose_name': 'Collocazione veicolo',
                'verbose_name_plural': 'Collocazioni veicolo',
            },
        ),
        migrations.CreateModel(
            name='FermoTecnico',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(verbose_name='Fine', blank=True, default=None, null=True, db_index=True)),
            ],
            options={
                'verbose_name': 'Fermo tecnico',
                'verbose_name_plural': 'Fermi tecnici',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('richiedente', models.ForeignKey(to='anagrafica.Sede', related_name='immatricolazioni_richieste')),
                ('ufficio', models.ForeignKey(to='anagrafica.Sede', related_name='immatricolazioni_istruite')),
            ],
            options={
                'verbose_name': 'Pratica di Immatricolazione',
                'verbose_name_plural': 'Pratiche di Immatricolazione',
            },
        ),
        migrations.CreateModel(
            name='Manutenzione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.PositiveIntegerField(verbose_name='Num. rifornimento', default=1, db_index=True)),
                ('data', models.DateTimeField(verbose_name='Data rifornimento', db_index=True)),
                ('contachilometri', models.PositiveIntegerField(verbose_name='Contachilometri', db_index=True)),
                ('consumo_carburante', models.FloatField(verbose_name='Consumo carburante lt.', blank=True, default=None, null=True, db_index=True)),
                ('consumo_olio_m', models.FloatField(verbose_name='Consumo Olio motori Kg.', blank=True, default=None, null=True, db_index=True)),
                ('consumo_olio_t', models.FloatField(verbose_name='Consumo Olio trasmissioni Kg.', blank=True, default=None, null=True, db_index=True)),
                ('consumo_olio_i', models.FloatField(verbose_name='Consumo Olio idraulico Kg.', blank=True, default=None, null=True, db_index=True)),
                ('presso', models.CharField(verbose_name='Presso', default='D', max_length=1, choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')])),
                ('contalitri', models.FloatField(verbose_name='(c/o Cisterna int.) Contalitri', blank=True, default=None, null=True, db_index=True)),
                ('ricevuta', models.CharField(blank=True, default=None, verbose_name='(c/o Distributore) N. Ricevuta', null=True, max_length=32, db_index=True)),
                ('conducente', models.ForeignKey(to='anagrafica.Persona', related_name='rifornimenti')),
            ],
            options={
                'verbose_name': 'Rifornimento di carburante',
                'verbose_name_plural': 'Rifornimenti di carburante',
            },
        ),
        migrations.CreateModel(
            name='Segnalazione',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('descrizione', models.TextField(verbose_name='Descrizione', max_length=1024)),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='segnalazioni')),
                ('manutenzione', models.ForeignKey(blank=True, to='veicoli.Manutenzione', null=True, related_name='segnalazioni')),
            ],
            options={
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(verbose_name='Stato', default='OK', max_length=2, choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')])),
                ('libretto', models.CharField(verbose_name='N. Libretto', max_length=16, help_text='Formato 201X-XXXXXXXXX', db_index=True)),
                ('targa', models.CharField(verbose_name='Targa (A)', max_length=5, help_text='Targa del Veicolo, senza spazi.', db_index=True)),
                ('formato_targa', models.CharField(verbose_name='Formato Targa', default='A', max_length=1, choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')])),
                ('prima_immatricolazione', models.DateField(verbose_name='Prima Immatricolazione (B)', db_index=True)),
                ('proprietario_cognome', models.CharField(verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', default='Croce Rossa Italiana', max_length=127)),
                ('proprietario_nome', models.CharField(verbose_name='Proprietario: Nome o Iniziale (C2.2)', default='Comitato Centrale', max_length=127)),
                ('proprietario_indirizzo', models.CharField(verbose_name='Proprietario: Indirizzo (C2.3)', default='Via Toscana, 12, 00187 Roma (RM), Italia', max_length=127)),
                ('pneumatici_anteriori', models.CharField(verbose_name='Pneumatici: Anteriori', max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_posteriori', models.CharField(verbose_name='Pneumatici: Posteriori', max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_alt_anteriori', models.CharField(verbose_name='Pneumatici alternativi: Anteriori', blank=True, null=True, max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_alt_posteriori', models.CharField(verbose_name='Pneumatici alternativi: Posteriori', blank=True, null=True, max_length=32, help_text='es. 215/70 R12C')),
                ('cambio', models.CharField(verbose_name='Cambio', default='Meccanico', max_length=32, help_text='Tipologia di Cambio')),
                ('lunghezza', models.FloatField(verbose_name='Lunghezza m.', blank=True, null=True)),
                ('larghezza', models.FloatField(verbose_name='Larghezza m.', blank=True, null=True)),
                ('sbalzo', models.FloatField(verbose_name='Sbalzo m.', blank=True, null=True)),
                ('tara', models.PositiveIntegerField(verbose_name='Tara kg.', blank=True, null=True)),
                ('marca', models.CharField(verbose_name='Marca (D.1)', max_length=32, help_text='es. Fiat')),
                ('modello', models.CharField(verbose_name='Tipo (D.2)', max_length=32, help_text='es. Ducato')),
                ('telaio', models.CharField(verbose_name='Numero Identificazione Veicolo (E)', unique=True, max_length=24, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', db_index=True)),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(verbose_name='Data immatricolazione attuale (I)', db_index=True)),
                ('categoria', models.CharField(verbose_name='Categoria del Veicolo (J)', max_length=16, help_text='es. Ambulanza', db_index=True)),
                ('destinazione', models.CharField(verbose_name='Destinazione ed uso (J.1)', max_length=32, help_text='es. Amb. Soccorso (AMB-A)')),
                ('carrozzeria', models.CharField(verbose_name='Carrozzeria (J.2)', max_length=16, help_text='es. Chiuso')),
                ('omologazione', models.CharField(verbose_name='N. Omologazione (K)', blank=True, null=True, max_length=32, help_text='es. OEXXXXXXXXXX')),
                ('num_assi', models.PositiveSmallIntegerField(verbose_name='Num. Assi (L)', default=2)),
                ('rimorchio_frenato', models.FloatField(verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', blank=True, null=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(verbose_name='Alimentazione (P.3)', default='B', max_length=1, choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')])),
                ('posti', models.SmallIntegerField(verbose_name='N. Posti a sedere conducente compreso (S.1)', default=5)),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(verbose_name='N. Card Rifornimento', blank=True, null=True, max_length=64)),
                ('selettiva_radio', models.CharField(verbose_name='Selettiva Radio', blank=True, null=True, max_length=64)),
                ('telepass', models.CharField(verbose_name='Numero Telepass', blank=True, null=True, max_length=64)),
                ('intervallo_revisione', models.PositiveIntegerField(verbose_name='Intervallo Revisione', default=365, choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')])),
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
            field=models.ForeignKey(blank=True, default=None, to='veicoli.Segnalazione', null=True, help_text='Rapporto conducente'),
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
