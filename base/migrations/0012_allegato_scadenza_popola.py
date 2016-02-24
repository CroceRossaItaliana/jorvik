# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.db.models import Q


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Allegato = apps.get_model("base", "Allegato")
    db_alias = schema_editor.connection.alias

    giorno_migrazione = datetime.datetime(2016, 2, 25)
    scadenza = datetime.datetime(2016, 2, 24)
    allegati = Allegato.objects.filter(
        creazione__lt=giorno_migrazione
    )
    numero = allegati.count()
    print("  => base-0012 ci sono %d allegati senza scadenza per i quali verra popolata" % (numero,))
    allegati.update(scadenza=scadenza)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_allegato_scadenza'),

    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
