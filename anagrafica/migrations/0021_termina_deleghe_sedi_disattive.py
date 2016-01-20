# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.db.models import Q


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Persona = apps.get_model("anagrafica", "Persona")
    Sede = apps.get_model("anagrafica", "Sede")
    Delega = apps.get_model("anagrafica", "Delega")
    db_alias = schema_editor.connection.alias

    # Questa migrazione ripristina tutte le deleghe
    # di ufficio soci che, alla data della migrazione,
    # erano assegnate a una unita' territoriale, modificandole
    # e ripristinandole come UFFICIO_SOCI_UNITA piuttosto che UFFICIO_SOCI.


    # da US a UU
    #pp = p.objects.using(db_alias).filter(email_contatto__exact='').exclude(utenza__email__isnull=True)
    #tot = pp.count()
    giorno_migrazione = datetime.date(2016, 1, 20)
    deleghe = Delega.objects.filter(
        Q(inizio__lte=giorno_migrazione),
        Q(Q(fine__isnull=True) | Q(fine__gt=giorno_migrazione)),
        oggetto_tipo__app_label="anagrafica",
        oggetto_tipo__model="sede",
        oggetto_id__in=Sede.objects.filter(attiva=False).values_list('id', flat=True)
    )
    numero = deleghe.count()
    tot = 0
    print("  => 0021 ci sono %d deleghe attive presso sedi non piu attive" % (numero,))
    for delega in deleghe:
        delega.fine = giorno_migrazione
        delega.save()
        tot += 1
    print("  ==> 0021 terminate %d deleghe attive presso sedi non piu attive" % (tot,))



class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0020_ripristino_deleghe_locali'),

    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
