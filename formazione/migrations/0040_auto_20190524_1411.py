# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-05-24 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formazione', '0039_auto_20190521_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corsoestensione',
            name='segmento',
            field=models.CharField(blank=True, choices=[('A', 'Tutti gli utenti di Gaia'), ('B', 'Volontari'), ('C', 'Volontari da meno di un anno'), ('D', 'Volontari da più di un anno'), ('E', 'Volontari con meno di 33 anni'), ('F', 'Volontari con 33 anni o più'), ('G', 'Sostenitori CRI'), ('H', 'Aspiranti volontari iscritti a un corso'), ('I', 'Tutti i Presidenti'), ('J', 'Presidenti di Comitati Locali'), ('K', 'Presidenti di Comitati Regionali'), ('IC', 'Tutti i Commissari'), ('JC', 'Commissari di Comitati Locali'), ('KC', 'Commissari di Comitati Regionali'), ('L', 'Delegati US'), ('M', 'Delegati Obiettivo I'), ('N', 'Delegati Obiettivo II'), ('O', 'Delegati Obiettivo III'), ('P', 'Delegati Obiettivo IV'), ('Q', 'Delegati Obiettivo V'), ('R', 'Delegati Obiettivo VI'), ('S', 'Referenti di un’Attività di Area I'), ('T', 'Referenti di un’Attività di Area II'), ('U', 'Referenti di un’Attività di Area III'), ('V', 'Referenti di un’Attività di Area IV'), ('W', 'Referenti di un’Attività di Area V'), ('X', 'Referenti di un’Attività di Area VI'), ('Y', 'Delegati Autoparco'), ('Z', 'Delegati Formazione'), ('AA', 'Volontari aventi un dato titolo')], max_length=9),
        ),
    ]