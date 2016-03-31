# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Sede = apps.get_model("anagrafica", "Sede")

    ex_locali = Sede.objects.filter(nome__contains="Locale")
    ex_provinciali = Sede.objects.filter(nome__contains="Provinciale")

    comitati = ex_locali | ex_provinciali
    comitati = comitati.order_by('nome')

    # print("")
    # print("| Ragione sociale originale | Nuova ragione sociale |")
    # print("|----------|----------|")
    for l in comitati:
        vecchio_nome = l.nome
        nuovo_nome = vecchio_nome\
                     .replace("Comitato Provinciale Di Roma", "Comitato dell'Area Metropolitana di Roma Capitale")\
                     .replace("Comitato Provinciale Di Trento", "Comitato della Provincia Autonoma di Trento")\
                     .replace("Comitato Provinciale Di Bolzano", "Comitato della Provincia Autonoma di Bolzano")\
                     .replace(" Locale", "")\
                     .replace(" Provinciale", "")\
                     .replace(" Di ", " di ").replace(" Della ", " della ").replace(" Dell'", " dell'").replace(" Delle ", " delle ")
        if vecchio_nome != nuovo_nome:
            # print("| %s | %s |" % (vecchio_nome, nuovo_nome))
            l.nome = nuovo_nome
            l.save()


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0038_auto_20160320_0254'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
