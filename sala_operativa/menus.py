from django.core.urlresolvers import reverse


def sala_operativa(me):
    # todo: new permessi ... ???
    from anagrafica.permessi.costanti import (GESTIONE_ATTIVITA,
                                              GESTIONE_ATTIVITA_AREA,
                                              GESTIONE_AREE_SEDE,
                                              GESTIONE_ATTIVITA_SEDE, )

    if me and me.volontario:
        servizio_area_exists = me and me.oggetti_permesso(GESTIONE_ATTIVITA_AREA).exists()

        return (
            ("Servizi", (
                ("Miei turni", "fa-list", reverse('so:storico')),
                ("Reperibilità", 'fa-thumbtack', reverse('so:reperibilita')),
                ("Calendario", "fa-calendar", reverse('so:calendario')),
                # ("Gruppi di lavoro", "fa-users", reverse('so:gruppo')),
                # ("Turni", 'fa-calendar', reverse('so:turni')),
                # ("Poteri", 'fa-magic', reverse('so:poteri')),
            )),

            ('Sala Operativa', (
                # ("Gruppi di lavoro", "fas fa-pencil-ruler", reverse('so:gruppo')) if servizio_area_exists else None,
                ("Organizza servizi", "fa-asterisk", reverse('so:organizza')) if servizio_area_exists else None,
                ("Mezzi e materiali", "fas fa-ambulance", reverse('so:mezzi')) if servizio_area_exists else None,
                ("Reperibilità dei Volontari", 'fa-user', reverse('so:reperibilita_backup')),
                ("Elenco servizi", "fa-list", reverse('so:gestisci')) if me.oggetti_permesso(GESTIONE_ATTIVITA).exists() else None,
                ("Aree di intervento", "fa-list", reverse('so:aree')) if me.oggetti_permesso(GESTIONE_AREE_SEDE).exists() else None,
                ("Statistiche", "far fa-chart-bar", reverse('so:statistiche')) if me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE).exists() else None,
            ))
        )
    else:
        return None
