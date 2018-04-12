# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from django.db import migrations, models
from django.db.models import Q


def nega_partecipazioni_vecchie(apps, schema_editor):

    Partecipazione = apps.get_model("attivita", "Partecipazione")
    Autorizzazione = apps.get_model("base", "Autorizzazione")

    partecipzioni_pendenti = Partecipazione.objects.filter(confermata=False, ritirata=False, automatica=False)
    totale = partecipzioni_pendenti.count()
    print("  => 0018 trovate %d partecipazioni di attivita pendenti" % (totale))

    autorizzazioni_con_scadenza = 0
    autorizzazioni_senza_scadenza = 0
    for partecipazione in partecipzioni_pendenti:
        # Autorizzazioni senza esito della partecipazione pendente
        autorizzazioni_partecipazione = Autorizzazione.objects.filter(oggetto_id=partecipazione.pk, concessa=None)
        for autorizzazione in autorizzazioni_partecipazione:
            # Se l'autorizzazione ha una scadenza
            if autorizzazione.scadenza:
                # Imposta negazione automatica per autorizzazione con scadenza
                if(autorizzazione.tipo_gestione != 'N'):
                    autorizzazione.tipo_gestione = 'N'
                    autorizzazione.save()
                    autorizzazioni_con_scadenza += 1
            else:
                # Imposta negazione automatica e scadenza 30gg per autorizzazione senza scadenza
                autorizzazione.tipo_gestione = 'N'
                autorizzazione.scadenza = autorizzazione.creazione + timedelta(days=30)
                autorizzazione.save()
                autorizzazioni_senza_scadenza += 1

    print("  ==> 0018 modificate %d autorizzazioni con scadenza e %d autorizzazioni senza scadenza" % (autorizzazioni_con_scadenza, autorizzazioni_senza_scadenza))


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0017_chiudi_attivita_vecchie'),
        ('base', '0018_autorizzazione_automatica'),
    ]

    operations = [
        migrations.RunPython(nega_partecipazioni_vecchie)
    ]
