# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('anagrafica', '0002_auto_20151102_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autoparco',
            fields=[
                ('conestensione_ptr', models.OneToOneField(to='base.ConEstensione', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(verbose_name='Fine', default=None, null=True, db_index=True, blank=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inizio', models.DateField(verbose_name='Inizio', db_index=True)),
                ('fine', models.DateField(verbose_name='Fine', default=None, null=True, db_index=True, blank=True)),
            ],
            options={
                'verbose_name': 'Fermo tecnico',
                'verbose_name_plural': 'Fermi tecnici',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('numero', models.PositiveIntegerField(verbose_name='Num. rifornimento', db_index=True, default=1)),
                ('data', models.DateTimeField(verbose_name='Data rifornimento', db_index=True)),
                ('contachilometri', models.PositiveIntegerField(verbose_name='Contachilometri', db_index=True)),
                ('consumo_carburante', models.FloatField(verbose_name='Consumo carburante lt.', default=None, null=True, db_index=True, blank=True)),
                ('consumo_olio_m', models.FloatField(verbose_name='Consumo Olio motori Kg.', default=None, null=True, db_index=True, blank=True)),
                ('consumo_olio_t', models.FloatField(verbose_name='Consumo Olio trasmissioni Kg.', default=None, null=True, db_index=True, blank=True)),
                ('consumo_olio_i', models.FloatField(verbose_name='Consumo Olio idraulico Kg.', default=None, null=True, db_index=True, blank=True)),
                ('presso', models.CharField(verbose_name='Presso', max_length=1, choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], default='D')),
                ('contalitri', models.FloatField(verbose_name='(c/o Cisterna int.) Contalitri', default=None, null=True, db_index=True, blank=True)),
                ('ricevuta', models.CharField(verbose_name='(c/o Distributore) N. Ricevuta', max_length=32, db_index=True, blank=True, null=True, default=None)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('descrizione', models.TextField(verbose_name='Descrizione', max_length=1024)),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='segnalazioni')),
                ('manutenzione', models.ForeignKey(blank=True, related_name='segnalazioni', null=True, to='veicoli.Manutenzione')),
            ],
            options={
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('stato', models.CharField(verbose_name='Stato', max_length=2, choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], default='OK')),
                ('libretto', models.CharField(verbose_name='N. Libretto', max_length=16, db_index=True, help_text='Formato 201X-XXXXXXXXX')),
                ('targa', models.CharField(verbose_name='Targa (A)', max_length=5, db_index=True, help_text='Targa del Veicolo, senza spazi.')),
                ('formato_targa', models.CharField(verbose_name='Formato Targa', max_length=1, choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], default='A')),
                ('prima_immatricolazione', models.DateField(verbose_name='Prima Immatricolazione (B)', db_index=True)),
                ('proprietario_cognome', models.CharField(verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', max_length=127, default='Croce Rossa Italiana')),
                ('proprietario_nome', models.CharField(verbose_name='Proprietario: Nome o Iniziale (C2.2)', max_length=127, default='Comitato Centrale')),
                ('proprietario_indirizzo', models.CharField(verbose_name='Proprietario: Indirizzo (C2.3)', max_length=127, default='Via Toscana, 12, 00187 Roma (RM), Italia')),
                ('pneumatici_anteriori', models.CharField(verbose_name='Pneumatici: Anteriori', max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_posteriori', models.CharField(verbose_name='Pneumatici: Posteriori', max_length=32, help_text='es. 215/70 R12C')),
                ('pneumatici_alt_anteriori', models.CharField(verbose_name='Pneumatici alternativi: Anteriori', help_text='es. 215/70 R12C', max_length=32, null=True, blank=True)),
                ('pneumatici_alt_posteriori', models.CharField(verbose_name='Pneumatici alternativi: Posteriori', help_text='es. 215/70 R12C', max_length=32, null=True, blank=True)),
                ('cambio', models.CharField(verbose_name='Cambio', help_text='Tipologia di Cambio', max_length=32, default='Meccanico')),
                ('lunghezza', models.FloatField(verbose_name='Lunghezza m.', null=True, blank=True)),
                ('larghezza', models.FloatField(verbose_name='Larghezza m.', null=True, blank=True)),
                ('sbalzo', models.FloatField(verbose_name='Sbalzo m.', null=True, blank=True)),
                ('tara', models.PositiveIntegerField(verbose_name='Tara kg.', null=True, blank=True)),
                ('marca', models.CharField(verbose_name='Marca (D.1)', max_length=32, help_text='es. Fiat')),
                ('modello', models.CharField(verbose_name='Tipo (D.2)', max_length=32, help_text='es. Ducato')),
                ('telaio', models.CharField(verbose_name='Numero Identificazione Veicolo (E)', unique=True, max_length=24, db_index=True, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX')),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(verbose_name='Data immatricolazione attuale (I)', db_index=True)),
                ('categoria', models.CharField(verbose_name='Categoria del Veicolo (J)', max_length=16, db_index=True, help_text='es. Ambulanza')),
                ('destinazione', models.CharField(verbose_name='Destinazione ed uso (J.1)', max_length=32, help_text='es. Amb. Soccorso (AMB-A)')),
                ('carrozzeria', models.CharField(verbose_name='Carrozzeria (J.2)', max_length=16, help_text='es. Chiuso')),
                ('omologazione', models.CharField(verbose_name='N. Omologazione (K)', help_text='es. OEXXXXXXXXXX', max_length=32, null=True, blank=True)),
                ('num_assi', models.PositiveSmallIntegerField(verbose_name='Num. Assi (L)', default=2)),
                ('rimorchio_frenato', models.FloatField(verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', null=True, blank=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(verbose_name='Alimentazione (P.3)', max_length=1, choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], default='B')),
                ('posti', models.SmallIntegerField(verbose_name='N. Posti a sedere conducente compreso (S.1)', default=5)),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(verbose_name='N. Card Rifornimento', max_length=64, null=True, blank=True)),
                ('selettiva_radio', models.CharField(verbose_name='Selettiva Radio', max_length=64, null=True, blank=True)),
                ('telepass', models.CharField(verbose_name='Numero Telepass', max_length=64, null=True, blank=True)),
                ('intervallo_revisione', models.PositiveIntegerField(verbose_name='Intervallo Revisione', choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], default=365)),
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
            field=models.ForeignKey(blank=True, null=True, help_text='Rapporto conducente', to='veicoli.Segnalazione', default=None),
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
