# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donatore',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('gruppo_sanguigno', models.CharField(max_length=3, db_index=True, choices=[('0', 'Gruppo 0'), ('A', 'Gruppo A'), ('B', 'Gruppo B'), ('AB', 'Gruppo AB')])),
                ('fattore_rh', models.CharField(max_length=2, db_index=True, choices=[('P', 'Positivo'), ('N', 'Negativo')], null=True)),
                ('fanotipo_rh', models.CharField(max_length=8, db_index=True, choices=[('CCDee', 'CCDee'), ('ccDEE', 'ccDEE'), ('CcDee', 'CcDee'), ('ccDEe', 'ccDEe'), ('ccDee', 'ccDee'), ('CCDEE', 'CCDEE'), ('CCDEe', 'CCDEe'), ('CcDEE', 'CcDEE'), ('CcDEe', 'CcDEe'), ('Ccddee', 'Ccddee'), ('CCddee', 'CCddee'), ('ccddEe', 'ccddEe'), ('ccddEE', 'ccddEE'), ('ccddee', 'ccddee'), ('CcddEe', 'CcddEe')], blank=True, null=True)),
                ('kell', models.CharField(max_length=16, blank=True, choices=[('K+k+', 'K+k+'), ('K+k-', 'K+k-'), ('K-k+', 'K-k+'), ('Kp(a+b+)', 'Kp(a+b+)'), ('Kp(a-b+)', 'Kp(a-b+)')], null=True)),
                ('codice_sit', models.CharField(db_index=True, max_length=32, blank=True, null=True)),
                ('persona', models.OneToOneField(related_name='donatore', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name_plural': 'Donatori di Sangue',
                'verbose_name': 'Donatore di Sangue',
            },
        ),
        migrations.CreateModel(
            name='Donazione',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('tipo', models.CharField(max_length=2, db_index=True, choices=[('DD', 'Donazione Differita'), ('SI', 'Sangue Intero'), ('PL', 'Plasmaferesi'), ('PP', 'PlasmaPiastrinoaferesi'), ('PI', 'Piastrinoaferesi'), ('EP', 'EritroPlasmaferesi'), ('2R', 'Doppi Globuli Rossi'), ('2P', 'Doppie Piastrine'), ('RP', 'Globuli Rossi e Piastrine'), ('MO', 'Midollo Osseo')])),
                ('data', models.DateField()),
                ('persona', models.ForeignKey(related_name='donazioni_sangue', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Merito',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('donazione', models.CharField(max_length=1, db_index=True, default='S', choices=[('S', 'Donazione di Sangue')])),
                ('merito', models.CharField(max_length=8, default='1', choices=[('1', '1'), ('10', '10'), ('20', '20'), ('40', '40')])),
                ('persona', models.ForeignKey(related_name='meriti_donazioni', to='anagrafica.Persona')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('citta', models.CharField(max_length=32)),
                ('provincia', models.CharField(max_length=32)),
                ('regione', models.CharField(max_length=32)),
                ('nome', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Sedi di Donazione Sangue',
                'ordering': ['regione', 'provincia', 'citta', 'nome'],
                'verbose_name': 'Sede di Donazione Sangue',
            },
        ),
        migrations.AddField(
            model_name='donazione',
            name='sede',
            field=models.ForeignKey(related_name='donazioni_sangue', to='sangue.Sede', null=True),
        ),
        migrations.AddField(
            model_name='donatore',
            name='sede_sit',
            field=models.ForeignKey(blank=True, to='sangue.Sede', null=True),
        ),
    ]
