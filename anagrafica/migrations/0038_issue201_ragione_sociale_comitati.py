# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    Sede = apps.get_model("anagrafica", "Sede")

    ex_locali = Sede.objects.filter(nome__contains="Locale")
    ex_provinciali = Sede.objects.filter(nome__contains="Provinciale")

    comitati = ex_locali | ex_provinciali

    for l in comitati:
        vecchio_nome = l.nome
        nuovo_nome = vecchio_nome.replace(" Locale", "").replace(" Provinciale", "")
        print("%s => %s" % (vecchio_nome, nuovo_nome))
        l.nome = nuovo_nome
        l.save()

    raise ValueError("Non pronto!")


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0037_auto_20160311_1814'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
