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
                ('conestensione_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='base.ConEstensione', serialize=False, auto_created=True)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(null=True, db_index=True, blank=True, verbose_name='Fine', default=None)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateField(null=True, db_index=True, blank=True, verbose_name='Fine', default=None)),
            ],
            options={
                'verbose_name_plural': 'Fermi tecnici',
                'verbose_name': 'Fermo tecnico',
            },
        ),
        migrations.CreateModel(
            name='Immatricolazione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('numero', models.PositiveIntegerField(db_index=True, verbose_name='Num. rifornimento', default=1)),
                ('data', models.DateTimeField(db_index=True, verbose_name='Data rifornimento')),
                ('contachilometri', models.PositiveIntegerField(db_index=True, verbose_name='Contachilometri')),
                ('consumo_carburante', models.FloatField(null=True, db_index=True, blank=True, verbose_name='Consumo carburante lt.', default=None)),
                ('consumo_olio_m', models.FloatField(null=True, db_index=True, blank=True, verbose_name='Consumo Olio motori Kg.', default=None)),
                ('consumo_olio_t', models.FloatField(null=True, db_index=True, blank=True, verbose_name='Consumo Olio trasmissioni Kg.', default=None)),
                ('consumo_olio_i', models.FloatField(null=True, db_index=True, blank=True, verbose_name='Consumo Olio idraulico Kg.', default=None)),
                ('presso', models.CharField(choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], max_length=1, verbose_name='Presso', default='D')),
                ('contalitri', models.FloatField(null=True, db_index=True, blank=True, verbose_name='(c/o Cisterna int.) Contalitri', default=None)),
                ('ricevuta', models.CharField(blank=True, max_length=32, null=True, db_index=True, verbose_name='(c/o Distributore) N. Ricevuta', default=None)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('descrizione', models.TextField(max_length=1024, verbose_name='Descrizione')),
                ('autore', models.ForeignKey(to='anagrafica.Persona', related_name='segnalazioni')),
                ('manutenzione', models.ForeignKey(blank=True, related_name='segnalazioni', to='veicoli.Manutenzione', null=True)),
            ],
            options={
                'verbose_name_plural': 'Segnalazioni di malfunzionamento o incidente',
                'verbose_name': 'Segnalazione di malfunzionamento o incidente',
            },
        ),
        migrations.CreateModel(
            name='Veicolo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(choices=[('IM', 'In immatricolazione'), ('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], max_length=2, verbose_name='Stato', default='OK')),
                ('libretto', models.CharField(db_index=True, help_text='Formato 201X-XXXXXXXXX', max_length=16, verbose_name='N. Libretto')),
                ('targa', models.CharField(db_index=True, help_text='Targa del Veicolo, senza spazi.', max_length=5, verbose_name='Targa (A)')),
                ('formato_targa', models.CharField(choices=[('A', 'Targa per Autoveicoli (A)'), ('B', 'Targa per Autoveicoli (B), per alloggiamenti viconlati'), ('C', 'Targa per Motoveicoli, Veicoli Speciali, Macchine Operatrici'), ('D', 'Targa per Rimorchi')], max_length=1, verbose_name='Formato Targa', default='A')),
                ('prima_immatricolazione', models.DateField(db_index=True, verbose_name='Prima Immatricolazione (B)')),
                ('proprietario_cognome', models.CharField(max_length=127, verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)', default='Croce Rossa Italiana')),
                ('proprietario_nome', models.CharField(max_length=127, verbose_name='Proprietario: Nome o Iniziale (C2.2)', default='Comitato Centrale')),
                ('proprietario_indirizzo', models.CharField(max_length=127, verbose_name='Proprietario: Indirizzo (C2.3)', default='Via Toscana, 12, 00187 Roma (RM), Italia')),
                ('pneumatici_anteriori', models.CharField(help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici: Anteriori')),
                ('pneumatici_posteriori', models.CharField(help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici: Posteriori')),
                ('pneumatici_alt_anteriori', models.CharField(null=True, blank=True, help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici alternativi: Anteriori')),
                ('pneumatici_alt_posteriori', models.CharField(null=True, blank=True, help_text='es. 215/70 R12C', max_length=32, verbose_name='Pneumatici alternativi: Posteriori')),
                ('cambio', models.CharField(help_text='Tipologia di Cambio', max_length=32, verbose_name='Cambio', default='Meccanico')),
                ('lunghezza', models.FloatField(null=True, blank=True, verbose_name='Lunghezza m.')),
                ('larghezza', models.FloatField(null=True, blank=True, verbose_name='Larghezza m.')),
                ('sbalzo', models.FloatField(null=True, blank=True, verbose_name='Sbalzo m.')),
                ('tara', models.PositiveIntegerField(null=True, blank=True, verbose_name='Tara kg.')),
                ('marca', models.CharField(help_text='es. Fiat', max_length=32, verbose_name='Marca (D.1)')),
                ('modello', models.CharField(help_text='es. Ducato', max_length=32, verbose_name='Tipo (D.2)')),
                ('telaio', models.CharField(db_index=True, help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', max_length=24, verbose_name='Numero Identificazione Veicolo (E)', unique=True)),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(db_index=True, verbose_name='Data immatricolazione attuale (I)')),
                ('categoria', models.CharField(db_index=True, help_text='es. Ambulanza', max_length=16, verbose_name='Categoria del Veicolo (J)')),
                ('destinazione', models.CharField(help_text='es. Amb. Soccorso (AMB-A)', max_length=32, verbose_name='Destinazione ed uso (J.1)')),
                ('carrozzeria', models.CharField(help_text='es. Chiuso', max_length=16, verbose_name='Carrozzeria (J.2)')),
                ('omologazione', models.CharField(null=True, blank=True, help_text='es. OEXXXXXXXXXX', max_length=32, verbose_name='N. Omologazione (K)')),
                ('num_assi', models.PositiveSmallIntegerField(verbose_name='Num. Assi (L)', default=2)),
                ('rimorchio_frenato', models.FloatField(null=True, blank=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.')),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], max_length=1, verbose_name='Alimentazione (P.3)', default='B')),
                ('posti', models.SmallIntegerField(verbose_name='N. Posti a sedere conducente compreso (S.1)', default=5)),
                ('regine', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(null=True, blank=True, max_length=64, verbose_name='N. Card Rifornimento')),
                ('selettiva_radio', models.CharField(null=True, blank=True, max_length=64, verbose_name='Selettiva Radio')),
                ('telepass', models.CharField(null=True, blank=True, max_length=64, verbose_name='Numero Telepass')),
                ('intervallo_revisione', models.PositiveIntegerField(choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], verbose_name='Intervallo Revisione', default=365)),
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
            field=models.ForeignKey(blank=True, to='veicoli.Segnalazione', null=True, help_text='Rapporto conducente', default=None),
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
