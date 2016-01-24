# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.db.models import Q


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Titolo = apps.get_model("curriculum", "Titolo")
    db_alias = schema_editor.connection.alias

    # Questa migrazione ripristina tutte le deleghe
    # di ufficio soci che, alla data della migrazione,
    # erano assegnate a una unita' territoriale, modificandole
    # e ripristinandole come UFFICIO_SOCI_UNITA piuttosto che UFFICIO_SOCI.


    # da US a UU
    #pp = p.objects.using(db_alias).filter(email_contatto__exact='').exclude(utenza__email__isnull=True)
    #tot = pp.count()
    giorno_migrazione = datetime.date(2016, 1, 22)
    titoli = Titolo.objects.filter(
        tipo="TS",
        richiede_codice=True,
        richiede_data_scadenza=True,
    )
    titoli.update(richiede_codice=False, richiede_data_scadenza=False)



class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0003_auto_20160118_2059'),

    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
