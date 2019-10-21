# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from django.db import migrations, models
from django.db.models import Q
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI


def nega_partecipazioni_vecchie(apps, schema_editor):

    Partecipazione = apps.get_model("attivita", "Partecipazione")
    Autorizzazione = apps.get_model("base", "Autorizzazione")

    # Ottieni ContentType per Partecipazione
    ContentType = apps.get_model("contenttypes", "ContentType")
    tipo = ContentType.objects.get_for_model(Partecipazione)

    # Costruisci primo oggetto Q, partecipazioni e relative autorizzazioni
    q1 = Q(confermata=False, ritirata=False, pk__in=Autorizzazione.objects.filter(oggetto_tipo__pk=tipo.id)
           .values_list('oggetto_id', flat=True))
    # Costruisci secondo oggetto Q, ci possono essere due autorizzazioni per una partecipazione
    q2 = ~Q(pk__in=Autorizzazione.objects.filter(oggetto_tipo__pk=tipo.id, concessa=False)
                                                 .values_list('oggetto_id', flat=True))

    # Autorizzazioni di partecipazioni pendenti
    autorizzazioni = Autorizzazione.objects.filter(oggetto_tipo_id=tipo.id,
                                                   oggetto_id__in=Partecipazione.objects.filter(q1,q2)
                                                   .values_list('id', flat=True))
    autorizzazioni.update(scadenza=datetime.now(), tipo_gestione="N")


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0017_chiudi_attivita_vecchie'),
        ('base', '0018_autorizzazione_automatica'),
    ]

    operations = [
        migrations.RunPython(nega_partecipazioni_vecchie)
    ]
