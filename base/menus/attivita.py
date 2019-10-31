def menu_attivita(me):
    from anagrafica.permessi.costanti import (GESTIONE_ATTIVITA,
        GESTIONE_ATTIVITA_AREA, GESTIONE_AREE_SEDE, GESTIONE_ATTIVITA_SEDE,)
    from attivita.models import Progetto
    from anagrafica.models import Delega
    from anagrafica.permessi.applicazioni import DELEGATO_PROGETTO
    from anagrafica.permessi.costanti import GESTIONE_SEDE

    if me and me.volontario:
        attivita_area_exists = me and me.oggetti_permesso(GESTIONE_ATTIVITA_AREA).exists()
        # Se si è presidenti/commissari/ufficio_soci
        # mostra il menu con tutti i progetti associati alle sedi gestite
        # altrimenti mostra solo i progetti di cui si è delegato
        if me.is_presidente or me.is_comissario:
            progetti_exists = Progetto.objects.filter(
                sede_id__in=me.oggetti_permesso(GESTIONE_SEDE, solo_deleghe_attive=True).values_list('id', flat=True)
            )
        else:
            progetti_exists = Progetto.objects.filter(
                id__in=Delega.objects.filter(tipo=DELEGATO_PROGETTO, persona=me).values_list('oggetto_id', flat=True)
            )

        return (
            ("Attività", (
                ("Calendario", "fa-calendar", "/attivita/calendario/"),
                ("Miei turni", "fa-list", "/attivita/storico/"),
                ("Gruppi di lavoro", "fa-users", "/attivita/gruppi/"),
                ("Reperibilità", "fa-thumb-tack", "/attivita/reperibilita/"),
            )),
            ("Gestione", (
                ("Aree di intervento/Progetti", "fa-list", "/attivita/aree/") if me.oggetti_permesso(GESTIONE_AREE_SEDE).exists() else None,

                ("Organizza attività", "fa-asterisk", "/attivita/organizza/") if attivita_area_exists else None,
                ("Elenco attività", "fa-list", "/attivita/gestisci/") if me.oggetti_permesso(GESTIONE_ATTIVITA).exists() else None,

                ("Organizza servizio", "fa-asterisk", "/attivita/servizio/organizza/") if progetti_exists else None,
                ("Elenco servizio", "fa-list", "/attivita/servizio/gestisci/") if progetti_exists else None,

                ("Gruppi di lavoro", "fa-pencil", "/attivita/gruppo/") if attivita_area_exists else None,
                ("Statistiche", "fa-bar-chart", "/attivita/statistiche/") if me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE).exists() else None,
            ))
        )
    else:
        return None
