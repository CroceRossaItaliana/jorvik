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
                ('conestensione_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, primary_key=True, to='base.ConEstensione')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, default=None, blank=True, verbose_name='Fine', null=True)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(db_index=True, default=None, blank=True, verbose_name='Fine', null=True)),
            ],
            options={
                'verbose_name_plural': 'Fermi tecnici',
                'verbose_name': 'Fermo tecnico',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.PositiveIntegerField(db_index=True, default=1, verbose_name='Num. rifornimento')),
                ('data', models.DateTimeField(db_index=True, verbose_name='Data rifornimento')),
                ('contachilometri', models.PositiveIntegerField(db_index=True, verbose_name='Contachilometri')),
                ('consumo_carburante', models.FloatField(db_index=True, default=None, blank=True, verbose_name='Consumo carburante lt.', null=True)),
                ('consumo_olio_m', models.FloatField(db_index=True, default=None, blank=True, verbose_name='Consumo Olio motori Kg.', null=True)),
                ('consumo_olio_t', models.FloatField(db_index=True, default=None, blank=True, verbose_name='Consumo Olio trasmissioni Kg.', null=True)),
                ('consumo_olio_i', models.FloatField(db_index=True, default=None, blank=True, verbose_name='Consumo Olio idraulico Kg.', null=True)),
                ('presso', models.CharField(default='D', verbose_name='Presso', choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], max_length=1)),
                ('contalitri', models.FloatField(db_index=True, default=None, blank=True, verbose_name='(c/o Cisterna int.) Contalitri', null=True)),
                ('ricevuta', models.CharField(db_index=True, default=None, blank=True, verbose_name='(c/o Distributore) N. Ricevuta', null=True, max_length=32)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('descrizione', models.TextField(verbose_name='Descrizione', max_length=1024)),
                ('autore', models.ForeignKey(related_name='segnalazioni', to='anagrafica.Persona')),
                ('manutenzione', models.ForeignKey(blank=True, null=True, related_name='segnalazioni', to='veicoli.Manutenzione')),
            ],
            options={
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(default='OK', verbose_name='Stato', choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], max_length=2)),
                ('libretto', models.CharField(db_index=True, help_text='Formato 201X-XXXXXXXXX', verbose_name='N. Libretto', max_length=16)),
                ('targa', models.CharField(db_index=True, help_text='Targa del Veicolo, senza spazi.', verbose_name='Targa (A)', max_length=5)),
                ('formato_targa', models.CharField(default='A', verbose_name='Formato Targa', choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], max_length=1)),
                ('prima_immatricolazione', models.DateField(db_index=True, verbose_name='Prima Immatricolazione (B)')),
                ('proprietario_cognome', models.CharField(default='Croce Rossa Italiana', verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', max_length=127)),
                ('proprietario_nome', models.CharField(default='Comitato Centrale', verbose_name='Proprietario: Nome o Iniziale (C2.2)', max_length=127)),
                ('proprietario_indirizzo', models.CharField(default='Via Toscana, 12, 00187 Roma (RM), Italia', verbose_name='Proprietario: Indirizzo (C2.3)', max_length=127)),
                ('pneumatici_anteriori', models.CharField(help_text='es. 215/70 R12C', verbose_name='Pneumatici: Anteriori', max_length=32)),
                ('pneumatici_posteriori', models.CharField(help_text='es. 215/70 R12C', verbose_name='Pneumatici: Posteriori', max_length=32)),
                ('pneumatici_alt_anteriori', models.CharField(null=True, blank=True, verbose_name='Pneumatici alternativi: Anteriori', help_text='es. 215/70 R12C', max_length=32)),
                ('pneumatici_alt_posteriori', models.CharField(null=True, blank=True, verbose_name='Pneumatici alternativi: Posteriori', help_text='es. 215/70 R12C', max_length=32)),
                ('cambio', models.CharField(help_text='Tipologia di Cambio', default='Meccanico', verbose_name='Cambio', max_length=32)),
                ('lunghezza', models.FloatField(null=True, blank=True, verbose_name='Lunghezza m.')),
                ('larghezza', models.FloatField(null=True, blank=True, verbose_name='Larghezza m.')),
                ('sbalzo', models.FloatField(null=True, blank=True, verbose_name='Sbalzo m.')),
                ('tara', models.PositiveIntegerField(null=True, blank=True, verbose_name='Tara kg.')),
                ('marca', models.CharField(help_text='es. Fiat', verbose_name='Marca (D.1)', max_length=32)),
                ('modello', models.CharField(help_text='es. Ducato', verbose_name='Tipo (D.2)', max_length=32)),
                ('telaio', models.CharField(db_index=True, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', unique=True, verbose_name='Numero Identificazione Veicolo (E)', max_length=24)),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(db_index=True, verbose_name='Data immatricolazione attuale (I)')),
                ('categoria', models.CharField(db_index=True, help_text='es. Ambulanza', verbose_name='Categoria del Veicolo (J)', max_length=16)),
                ('destinazione', models.CharField(help_text='es. Amb. Soccorso (AMB-A)', verbose_name='Destinazione ed uso (J.1)', max_length=32)),
                ('carrozzeria', models.CharField(help_text='es. Chiuso', verbose_name='Carrozzeria (J.2)', max_length=16)),
                ('omologazione', models.CharField(null=True, blank=True, verbose_name='N. Omologazione (K)', help_text='es. OEXXXXXXXXXX', max_length=32)),
                ('num_assi', models.PositiveSmallIntegerField(default=2, verbose_name='Num. Assi (L)')),
                ('rimorchio_frenato', models.FloatField(null=True, blank=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.')),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(default='B', verbose_name='Alimentazione (P.3)', choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], max_length=1)),
                ('posti', models.SmallIntegerField(default=5, verbose_name='N. Posti a sedere conducente compreso (S.1)')),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(null=True, blank=True, verbose_name='N. Card Rifornimento', max_length=64)),
                ('selettiva_radio', models.CharField(null=True, blank=True, verbose_name='Selettiva Radio', max_length=64)),
                ('telepass', models.CharField(null=True, blank=True, verbose_name='Numero Telepass', max_length=64)),
                ('intervallo_revisione', models.PositiveIntegerField(default=365, verbose_name='Intervallo Revisione', choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')])),
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
            field=models.ForeignKey(default=None, blank=True, help_text='Rapporto conducente', null=True, to='veicoli.Segnalazione'),
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
