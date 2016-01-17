# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import veicoli.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autoparco',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('estensione', models.CharField(max_length=1, db_index=True, choices=[('T', 'Unità Territoriale'), ('L', 'Sede Locale'), ('P', 'Sede Provinciale'), ('R', 'Sede Regionale'), ('N', 'Sede Nazionale')], verbose_name='Estensione')),
                ('nome', models.CharField(max_length=256)),
                ('telefono', models.CharField(blank=True, max_length=64, verbose_name='Telefono')),
                ('locazione', models.ForeignKey(related_name='veicoli_autoparco', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Locazione', null=True)),
                ('sede', models.ForeignKey(to='anagrafica.Sede')),
            ],
            options={
                'verbose_name_plural': 'Autoparchi',
            },
        ),
        migrations.CreateModel(
            name='Collocazione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('autoparco', models.ForeignKey(related_name='autoparco', to='veicoli.Autoparco')),
                ('creato_da', models.ForeignKey(related_name='collocazioni_veicoli', to='anagrafica.Persona', null=True)),
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
                ('inizio', models.DateTimeField(db_index=True, verbose_name='Inizio')),
                ('fine', models.DateTimeField(help_text='Lasciare il campo vuoto per impostare fine indeterminata.', db_index=True, verbose_name='Fine', blank=True, default=None, null=True)),
                ('motivo', models.CharField(max_length=512)),
                ('creato_da', models.ForeignKey(related_name='fermi_tecnici_creati', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Fermi tecnici',
                'verbose_name': 'Fermo tecnico',
            },
        ),
        migrations.CreateModel(
            name='Manutenzione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('tipo', models.CharField(max_length=1, db_index=True, default='O', choices=[('R', 'Revisione veicolo'), ('O', 'Manutenzione ordinaria veicolo'), ('S', 'Manutenzione straordinaria veicolo')])),
                ('data', models.DateField(db_index=True, validators=[veicoli.validators.valida_data_manutenzione])),
                ('descrizione', models.TextField(max_length=4096, null=True)),
                ('km', models.PositiveIntegerField()),
                ('manutentore', models.CharField(help_text='es. autoriparato', max_length=512)),
                ('numero_fattura', models.CharField(help_text='es. 122/A', max_length=64)),
                ('costo', models.PositiveIntegerField()),
                ('creato_da', models.ForeignKey(related_name='manutenzioni_registrate', to='anagrafica.Persona')),
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
                ('data', models.DateTimeField(db_index=True, verbose_name='Data rifornimento')),
                ('contachilometri', models.PositiveIntegerField(db_index=True, verbose_name='Contachilometri')),
                ('costo', models.FloatField(db_index=True, verbose_name='Costo')),
                ('consumo_carburante', models.FloatField(help_text='Litri di carburante immessi', db_index=True, default=0.0, verbose_name='Consumo carburante lt.')),
                ('presso', models.CharField(max_length=1, default=None, choices=[('I', 'Cisterna interna'), ('C', 'Distributore convenzionato'), ('D', 'Distributore occasionale')], verbose_name='Presso', null=True)),
                ('contalitri', models.FloatField(db_index=True, default=None, verbose_name='(c/o Cisterna int.) Contalitri', null=True)),
                ('ricevuta', models.CharField(db_index=True, verbose_name='(c/o Distributore) N. Ricevuta', blank=True, default=None, max_length=32, null=True)),
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
                ('autore', models.ForeignKey(related_name='segnalazioni', to='anagrafica.Persona')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('stato', models.CharField(max_length=2, default='OK', choices=[('OK', 'In servizio'), ('KO', 'Dismesso/Fuori uso')], verbose_name='Stato')),
                ('libretto', models.CharField(help_text='Formato 201X-XXXXXXXXX', db_index=True, max_length=32, verbose_name='N. Libretto')),
                ('targa', models.CharField(help_text='Targa del Veicolo, senza spazi.', db_index=True, max_length=16, verbose_name='Targa (A)')),
                ('prima_immatricolazione', models.DateField(db_index=True, verbose_name='Prima Immatricolazione (B)')),
                ('proprietario_cognome', models.CharField(default='Croce Rossa Italiana', max_length=127, verbose_name='Proprietario: Cognome o Ragione Sociale (C2.1)')),
                ('proprietario_nome', models.CharField(default='Comitato Centrale', max_length=127, verbose_name='Proprietario: Nome o Iniziale (C2.2)')),
                ('proprietario_indirizzo', models.CharField(default='Via Toscana, 12, 00187 Roma (RM), Italia', max_length=127, verbose_name='Proprietario: Indirizzo (C2.3)')),
                ('pneumatici_anteriori', models.CharField(help_text='es. 215/70 R12C', max_length=255, verbose_name='Pneumatici: Anteriori')),
                ('pneumatici_posteriori', models.CharField(help_text='es. 215/70 R12C', max_length=255, verbose_name='Pneumatici: Posteriori')),
                ('pneumatici_alt_anteriori', models.CharField(help_text='es. 215/70 R12C', blank=True, max_length=255, verbose_name='Pneumatici alternativi: Anteriori', null=True)),
                ('pneumatici_alt_posteriori', models.CharField(help_text='es. 215/70 R12C', blank=True, max_length=255, verbose_name='Pneumatici alternativi: Posteriori', null=True)),
                ('cambio', models.CharField(help_text='Tipologia di Cambio', default='Meccanico', max_length=32, verbose_name='Cambio')),
                ('lunghezza', models.FloatField(blank=True, verbose_name='Lunghezza m.', null=True)),
                ('larghezza', models.FloatField(blank=True, verbose_name='Larghezza m.', null=True)),
                ('sbalzo', models.FloatField(blank=True, verbose_name='Sbalzo m.', null=True)),
                ('tara', models.PositiveIntegerField(blank=True, verbose_name='Tara kg.', null=True)),
                ('marca', models.CharField(help_text='es. Fiat', max_length=32, verbose_name='Marca (D.1)')),
                ('modello', models.CharField(help_text='es. Ducato', max_length=32, verbose_name='Tipo (D.2)')),
                ('telaio', models.CharField(help_text='Numero di telaio del veicolo, es. ZXXXXXXXXXXXXXXX', db_index=True, verbose_name='Numero Identificazione Veicolo (E)', unique=True, max_length=64, null=True)),
                ('massa_max', models.PositiveIntegerField(verbose_name='Massa Massima a carico (F.2)')),
                ('data_immatricolazione', models.DateField(db_index=True, verbose_name='Data immatricolazione attuale (I)')),
                ('categoria', models.CharField(help_text='es. Ambulanza', db_index=True, max_length=128, verbose_name='Categoria del Veicolo (J)')),
                ('destinazione', models.CharField(help_text='es. Amb. Soccorso (AMB-A)', max_length=128, verbose_name='Destinazione ed uso (J.1)')),
                ('carrozzeria', models.CharField(help_text='es. Chiuso', max_length=128, verbose_name='Carrozzeria (J.2)')),
                ('omologazione', models.CharField(help_text='es. OEXXXXXXXXXX', blank=True, max_length=32, verbose_name='N. Omologazione (K)', null=True)),
                ('num_assi', models.PositiveIntegerField(default=2, verbose_name='Num. Assi (L)')),
                ('rimorchio_frenato', models.FloatField(blank=True, verbose_name='Massa massima a Rimorchio frenato tecnicamente ammissibile (O) kg.', null=True)),
                ('cilindrata', models.PositiveIntegerField(verbose_name='Cilindrata (P.1)')),
                ('potenza_massima', models.PositiveIntegerField(verbose_name='Potenza Massima (P.2) kW.')),
                ('alimentazione', models.CharField(max_length=1, default=None, choices=[('B', 'Benzina'), ('G', 'Gasolio'), ('P', 'GPL'), ('M', 'Metano'), ('E', 'Elettrica')], verbose_name='Alimentazione (P.3)', null=True)),
                ('posti', models.PositiveIntegerField(default=5, verbose_name='N. Posti a sedere conducente compreso (S.1)')),
                ('regime', models.PositiveIntegerField(verbose_name='Livello Sonoro: Regime del motore (U.2)')),
                ('card_rifornimento', models.CharField(blank=True, max_length=64, verbose_name='N. Card Rifornimento', null=True)),
                ('selettiva_radio', models.CharField(blank=True, max_length=64, verbose_name='Selettiva Radio', null=True)),
                ('telepass', models.CharField(blank=True, max_length=64, verbose_name='Numero Telepass', null=True)),
                ('intervallo_revisione', models.PositiveIntegerField(default=365, choices=[(365, '1 anno (365 giorni)'), (730, '2 anni (730 giorni)')], verbose_name='Intervallo Revisione')),
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
            name='veicolo',
            field=models.ForeignKey(related_name='rifornimenti', to='veicoli.Veicolo'),
        ),
        migrations.AddField(
            model_name='manutenzione',
            name='veicolo',
            field=models.ForeignKey(related_name='manutenzioni', to='veicoli.Veicolo'),
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
