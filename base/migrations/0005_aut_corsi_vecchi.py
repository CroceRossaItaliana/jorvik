# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.db.models import Q


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Autorizzazione = apps.get_model("base", "Autorizzazione")
    db_alias = schema_editor.connection.alias

    giorno_migrazione = datetime.date(2015, 9, 20)
    auts = Autorizzazione.objects.filter(
        destinatario_ruolo="CB-PART",
        creazione__lt=giorno_migrazione,
        ultima_modifica__lt=giorno_migrazione,
        concessa__isnull=True,
        necessaria=True
    )
    numero = auts.count()
    tot = 0
    print("  => base-0005 ci sono %d autorizzazioni corso più vecchie di sett. 2015 che verranno eliminate" % (numero,))
    auts.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20160120_1524'),

    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
