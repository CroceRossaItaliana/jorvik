# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-06-30 21:41
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('donazioni', '0010_auto_20170623_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='donatore',
            name='cap_residenza',
            field=models.CharField(blank=True, max_length=16, verbose_name='CAP di Residenza'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='cellulare',
            field=models.CharField(blank=True, max_length=64, verbose_name='Cellulare'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='comune_residenza',
            field=models.CharField(blank=True, max_length=64, verbose_name='Comune di residenza'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='fax',
            field=models.CharField(blank=True, max_length=64, verbose_name='FAX'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='indirizzo',
            field=models.CharField(blank=True, max_length=512, verbose_name='Indirizzo di residenza'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='lingua',
            field=models.CharField(blank=True, choices=[('IT', 'Italiano'), ('EN', 'Inglese'), ('FR', 'Francese'), ('ES', 'Spagnolo'), ('DE', 'Tedesco'), ('PR', 'Portoghese'), ('CH', 'Cinese Mandarino'), ('AR', 'Arabo')], max_length=2, verbose_name='Lingua'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='professione',
            field=models.CharField(blank=True, choices=[('STUD', 'Studente'), ('PENS', 'Pensionato'), ('IMP', 'Impiegato'), ('IMPR', 'Imprenditore'), ('LIBPROF', 'Libero Professionista'), ('-', 'Altra Professione')], max_length=10, verbose_name='Professione'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='provincia_residenza',
            field=models.CharField(blank=True, max_length=2, verbose_name='Provincia di residenza'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='sesso',
            field=models.CharField(blank=True, choices=[('M', 'Maschile'), ('F', 'Femminile')], max_length=1, verbose_name='Sesso'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='stato_residenza',
            field=django_countries.fields.CountryField(blank=True, max_length=2, verbose_name='Stato di residenza'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='telefono',
            field=models.CharField(blank=True, max_length=64, verbose_name='Telefono'),
        ),
        migrations.AddField(
            model_name='donatore',
            name='tipo_donatore',
            field=models.CharField(blank=True, choices=[('P', 'Privato'), ('A', 'Azienda'), ('C', 'CRI')], max_length=1, verbose_name='Tipo Donatore'),
        ),
    ]
