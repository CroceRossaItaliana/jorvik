from django.core.urlresolvers import reverse


def sala_operativa(me):
    from anagrafica.permessi.costanti import (GESTIONE_SERVIZI, GESTIONE_SO_SEDE, )

    if me and me.volontario:
        gestione_so = me and me.oggetti_permesso(GESTIONE_SO_SEDE).exists()

        return (
            ("Servizi", (
                ("Miei turni", "fa-list", reverse('so:storico')),
                ("Reperibilità", 'fa-thumbtack', reverse('so:reperibilita')),
                ("Calendario", "fa-calendar", reverse('so:calendario')),
                # ("Turni", 'fa-calendar', reverse('so:turni')),
                # ("Poteri", 'fa-magic', reverse('so:poteri')),
            )),

            ('Sala Operativa', (
                ("Organizza servizi", "fa-asterisk", reverse('so:organizza')) if gestione_so else None,
                ("Mezzi e materiali", "fas fa-ambulance", reverse('so:mezzi')) if gestione_so else None,
                ("Reperibilità dei Volontari", 'fa-user', reverse('so:reperibilita_backup')),
                ("Elenco servizi", "fa-list", reverse('so:gestisci')) if gestione_so else None,
                ("Statistiche", "far fa-chart-bar", reverse('so:statistiche')) if gestione_so else None,
            ))
        )
    else:
        return None
