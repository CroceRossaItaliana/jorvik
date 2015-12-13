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
                ('conestensione_ptr', models.OneToOneField(primary_key=True, serialize=False, parent_link=True, auto_created=True, to='base.ConEstensione')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(blank=True, default=None, null=True, db_index=True, verbose_name='Fine')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(blank=True, default=None, null=True, db_index=True, verbose_name='Fine')),
            ],
            options={
                'verbose_name_plural': 'Fermi tecnici',
                'verbose_name': 'Fermo tecnico',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Interventi di Manutenzione',
                'verbose_name': 'Intervento di Manutenzione',
            },
        ),
        migrations.CreateModel(
            name='Rifornimento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.PositiveIntegerField(default=1, db_index=True, verbose_name='Num. rifornimento')),
                ('data', models.DateTimeField(db_index=True, verbose_name='Data rifornimento')),
                ('contachilometri', models.PositiveIntegerField(db_index=True, verbose_name='Contachilometri')),
                ('consumo_carburante', models.FloatField(blank=True, default=None, null=True, db_index=True, verbose_name='Consumo carburante lt.')),
                ('consumo_olio_m', models.FloatField(blank=True, default=None, null=True, db_index=True, verbose_name='Consumo Olio motori Kg.')),
                ('consumo_olio_t', models.FloatField(blank=True, default=None, null=True, db_index=True, verbose_name='Consumo Olio trasmissioni Kg.')),
                ('consumo_olio_i', models.FloatField(blank=True, default=None, null=True, db_index=True, verbose_name='Consumo Olio idraulico Kg.')),
                ('presso', models.CharField(choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], default='D', max_length=1, verbose_name='Presso')),
                ('contalitri', models.FloatField(blank=True, default=None, null=True, db_index=True, verbose_name='(c/o Cisterna int.) Contalitri')),
                ('ricevuta', models.CharField(default=None, blank=True, db_index=True, null=True, max_length=32, verbose_name='(c/o Distributore) N. Ricevuta')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('descrizione', models.TextField(max_length=1024, verbose_name='Descrizione')),
                ('autore', models.ForeignKey(related_name='segnalazioni', to='anagrafica.Persona')),
                ('manutenzione', models.ForeignKey(related_name='segnalazioni', blank=True, null=True, to='veicoli.Manutenzione')),
            ],
            options={
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], default='OK', max_length=2, verbose_name='Stato')),
                ('libretto', models.CharField(max_length=16, db_index=True, help_text='Formato 201X-XXXXXXXXX', verbose_name='N. Libretto')),
                ('targa', models.CharField(max_length=5, db_index=True, help_text='Targa del Veicolo, senza spazi.', verbose_name='Targa (A)')),
                ('formato_targa', models.CharField(choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], default='A', max_length=1, verbose_name='Formato Targa')),
                ('prima_immatricolazione', models.DateField(db_index=True, verbose_name='Prima Immatricolazione (B)')),
                ('proprietario_cognome', models.CharField(default='Croce Rossa Italiana', max_length=127, verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)')),
                ('proprietario_nome', models.CharField(default='Comitato Centrale', max_length=127, verbose_name='Proprietario: Nome o Iniziale (C2.2)')),
                ('proprietario_indirizzo', models.CharField(default='Via Toscana, 12, 00187 Roma (RM), Italia', max_length=127, verbose_name='Proprietario: Indirizzo (C2.3)')),
                ('pneumatici_anteriori', models.CharField(max_length=32, help_text='es. 215/70 R12C', verbose_name='Pneumatici: Anteriori')),
                ('pneumatici_posteriori', models.CharField(max_length=32, help_text='es. 215/70 R12C', verbose_name='Pneumatici: Posteriori')),
                ('pneumatici_alt_anteriori', models.CharField(blank=True, max_length=32, null=True, help_text='es. 215/70 R12C', verbose_name='Pneumatici alternativi: Anteriori')),
                ('pneumatici_alt_posteriori', models.CharField(blank=True, max_length=32, null=True, help_text='es. 215/70 R12C', verbose_name='Pneumatici alternativi: Posteriori')),
                ('cambio', models.CharField(max_length=32, default='Meccanico', help_text='Tipologia di Cambio', verbose_name='Cambio')),
                ('lunghezza', models.FloatField(blank=True, null=True, verbose_name='Lunghezza m.')),
                ('larghezza', models.FloatField(blank=True, null=True, verbose_name='Larghezza m.')),
                ('sbalzo', models.FloatField(blank=True, null=True, verbose_name='Sbalzo m.')),
                ('tara', models.PositiveIntegerField(blank=True, null=True, verbose_name='Tara kg.')),
                ('marca', models.CharField(max_length=32, help_text='es. Fiat', verbose_name='Marca (D.1)')),
                ('modello', models.CharField(max_length=32, help_text='es. Ducato', verbose_name='Tipo (D.2)')),
                ('telaio', models.CharField(max_length=24, verbose_name='Numero Identificazione Veicolo (E)', db_index=True, unique=True, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX')),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(db_index=True, verbose_name='Data immatricolazione attuale (I)')),
                ('categoria', models.CharField(max_length=16, db_index=True, help_text='es. Ambulanza', verbose_name='Categoria del Veicolo (J)')),
                ('destinazione', models.CharField(max_length=32, help_text='es. Amb. Soccorso (AMB-A)', verbose_name='Destinazione ed uso (J.1)')),
                ('carrozzeria', models.CharField(max_length=16, help_text='es. Chiuso', verbose_name='Carrozzeria (J.2)')),
                ('omologazione', models.CharField(blank=True, max_length=32, null=True, help_text='es. OEXXXXXXXXXX', verbose_name='N. Omologazione (K)')),
                ('num_assi', models.PositiveSmallIntegerField(default=2, verbose_name='Num. Assi (L)')),
                ('rimorchio_frenato', models.FloatField(blank=True, null=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.')),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], default='B', max_length=1, verbose_name='Alimentazione (P.3)')),
                ('posti', models.SmallIntegerField(default=5, verbose_name='N. Posti a sedere conducente compreso (S.1)')),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(blank=True, null=True, max_length=64, verbose_name='N. Card Rifornimento')),
                ('selettiva_radio', models.CharField(blank=True, null=True, max_length=64, verbose_name='Selettiva Radio')),
                ('telepass', models.CharField(blank=True, null=True, max_length=64, verbose_name='Numero Telepass')),
                ('intervallo_revisione', models.PositiveIntegerField(choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], default=365, verbose_name='Intervallo Revisione')),
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
            field=models.ForeignKey(default=None, blank=True, null=True, help_text='Rapporto conducente', to='veicoli.Segnalazione'),
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
