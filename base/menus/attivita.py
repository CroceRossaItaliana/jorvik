def menu_attivita(me):
    from anagrafica.permessi.costanti import (GESTIONE_ATTIVITA,
        GESTIONE_ATTIVITA_AREA, GESTIONE_AREE_SEDE, GESTIONE_ATTIVITA_SEDE,)

    if me and me.volontario:
        attivita_area_exists = me and me.oggetti_permesso(GESTIONE_ATTIVITA_AREA).exists()

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

                ("Organizza servizio", "fa-asterisk", "/servizio/organizza/") if attivita_area_exists else None,
                ("Elenco servizio", "fa-list", "/servizio/gestisci/") if me.oggetti_permesso(GESTIONE_ATTIVITA).exists() else None,

                ("Gruppi di lavoro", "fa-pencil", "/attivita/gruppo/") if attivita_area_exists else None,
                ("Statistiche", "fa-bar-chart", "/attivita/statistiche/") if me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE).exists() else None,
            ))
        )
    else:
        return None
