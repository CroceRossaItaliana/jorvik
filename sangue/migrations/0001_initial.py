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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('gruppo_sanguigno', models.CharField(choices=[('0', 'Gruppo 0'), ('A', 'Gruppo A'), ('B', 'Gruppo B'), ('AB', 'Gruppo AB')], max_length=3, db_index=True)),
                ('fattore_rh', models.CharField(choices=[('P', 'Positivo'), ('N', 'Negativo')], max_length=2, null=True, db_index=True)),
                ('fanotipo_rh', models.CharField(blank=True, choices=[('CCDee', 'CCDee'), ('ccDEE', 'ccDEE'), ('CcDee', 'CcDee'), ('ccDEe', 'ccDEe'), ('ccDee', 'ccDee'), ('CCDEE', 'CCDEE'), ('CCDEe', 'CCDEe'), ('CcDEE', 'CcDEE'), ('CcDEe', 'CcDEe'), ('Ccddee', 'Ccddee'), ('CCddee', 'CCddee'), ('ccddEe', 'ccddEe'), ('ccddEE', 'ccddEE'), ('ccddee', 'ccddee'), ('CcddEe', 'CcddEe')], max_length=8, null=True, db_index=True)),
                ('kell', models.CharField(blank=True, choices=[('K+k+', 'K+k+'), ('K+k-', 'K+k-'), ('K-k+', 'K-k+'), ('Kp(a+b+)', 'Kp(a+b+)'), ('Kp(a-b+)', 'Kp(a-b+)')], max_length=16, null=True)),
                ('codice_sit', models.CharField(max_length=32, blank=True, null=True, db_index=True)),
                ('persona', models.OneToOneField(related_name='donatore', to='anagrafica.Persona')),
            ],
            options={
                'verbose_name': 'Donatore di Sangue',
                'verbose_name_plural': 'Donatori di Sangue',
            },
        ),
        migrations.CreateModel(
            name='Donazione',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', default=True, db_index=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', default=False, db_index=True)),
                ('tipo', models.CharField(choices=[('DD', 'Donazione Differita'), ('SI', 'Sangue Intero'), ('PL', 'Plasmaferesi'), ('PP', 'PlasmaPiastrinoaferesi'), ('PI', 'Piastrinoaferesi'), ('EP', 'EritroPlasmaferesi'), ('2R', 'Doppi Globuli Rossi'), ('2P', 'Doppie Piastrine'), ('RP', 'Globuli Rossi e Piastrine'), ('MO', 'Midollo Osseo')], max_length=2, db_index=True)),
                ('data', models.DateField()),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='donazioni_sangue')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Merito',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('donazione', models.CharField(max_length=1, choices=[('S', 'Donazione di Sangue')], default='S', db_index=True)),
                ('merito', models.CharField(max_length=8, choices=[('1', '1'), ('10', '10'), ('20', '20'), ('40', '40')], default='1')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='meriti_donazioni')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sede',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('citta', models.CharField(max_length=32)),
                ('provincia', models.CharField(max_length=32)),
                ('regione', models.CharField(max_length=32)),
                ('nome', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Sede di Donazione Sangue',
                'ordering': ['regione', 'provincia', 'citta', 'nome'],
                'verbose_name_plural': 'Sedi di Donazione Sangue',
            },
        ),
        migrations.AddField(
            model_name='donazione',
            name='sede',
            field=models.ForeignKey(to='sangue.Sede', related_name='donazioni_sangue', null=True),
        ),
        migrations.AddField(
            model_name='donatore',
            name='sede_sit',
            field=models.ForeignKey(to='sangue.Sede', blank=True, null=True),
        ),
    ]
