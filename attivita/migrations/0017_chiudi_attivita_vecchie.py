# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from django.db import migrations, models
from django.db.models import Q


def forward_func(apps, schema_editor):

    Attivita = apps.get_model("attivita", "Attivita")
    Turno = apps.get_model("attivita", "Turno")
    Delega = apps.get_model("anagrafica", "Delega")

    # Trova tutte le attivita vecchie
    GIORNI = 60
    poco_fa = datetime.now()
    giorni_fa = poco_fa - timedelta(days=GIORNI)

    atts = Attivita.objects.all()
    totale = atts.count()
    ids = []
    print("  => 0021 trovate %d attivita piu vecchie di %d giorni" % (totale, GIORNI,))

    for att in atts:

        ultimo_turno = Turno.objects.filter(attivita_id=att.pk).order_by('-fine').first()
        if not ultimo_turno:
            continue

        if ultimo_turno.fine < giorni_fa:
            ids.append(att.pk)

    # Chiudi attivita
    Attivita.objects.filter(id__in=ids).update(apertura="C",
                                               chiusa_automaticamente=poco_fa)

    # Sospendi deleghe
    Delega.objects.filter(oggetto_tipo__app_label="attivita",
                          oggetto_tipo__model="attivita",
                          oggetto_id__in=ids)\
                  .update(stato="s")

    print("  ==> 0021 chiuse %d di %d attivita" % (len(ids), totale))


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0016_attivita_chiusa_automaticamente'),
    ]

    operations = [
        migrations.RunPython(forward_func)
    ]
