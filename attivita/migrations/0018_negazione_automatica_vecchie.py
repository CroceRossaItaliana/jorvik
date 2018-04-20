# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from django.db import migrations, models
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI


def nega_partecipazioni_vecchie(apps, schema_editor):

    Autorizzazione = apps.get_model("base", "Autorizzazione")

    # Autorizzazioni attività di partecipazione, senza esito ed escludendo quelle già negate.
    autorizzazioni = Autorizzazione.objects.filter(concessa__isnull=True,
                                                   destinatario_ruolo=INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI
                                                  ).exclude(tipo_gestione="N")

    # Impostazione scadenza su data attuale e negazione automatica.
    autorizzazioni.update(scadenza=datetime.now(), tipo_gestione="N")


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0017_chiudi_attivita_vecchie'),
        ('base', '0018_autorizzazione_automatica'),
    ]

    operations = [
        migrations.RunPython(nega_partecipazioni_vecchie)
    ]
