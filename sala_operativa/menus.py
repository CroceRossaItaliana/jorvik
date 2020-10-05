from django.core.urlresolvers import reverse


def sala_operativa(me):
    from anagrafica.permessi.costanti import (GESTIONE_SERVIZI, GESTIONE_SO_SEDE, )

    if me and me.volontario:
        gestione_so = me.oggetti_permesso(GESTIONE_SO_SEDE).exists()
        gestione_servizi = me.oggetti_permesso(GESTIONE_SERVIZI).exists()

        return (
            ("Servizi", (
                ("Miei turni", "fa-list", reverse('so:storico')),
                ("Mie reperibilità", 'fa-thumbtack', reverse('so:reperibilita')),
                ("Calendario", "fa-calendar", reverse('so:calendario')),
            )),

            ('Sala Operativa', (
                ("Organizza servizi", "fa-asterisk", reverse('so:organizza')) if gestione_so else None,
                ("Mezzi e materiali", "fas fa-ambulance", reverse('so:mezzi')) if gestione_so else None,
                ("Reperibilità dei Volontari", 'fa-user', reverse('so:reperibilita_backup')) if gestione_so else None,
                ("Datore di lavore", "fa-edit", reverse('so:datore_di_lavoro')) if gestione_so else None,
                ("Elenco servizi", "fa-list", reverse('so:gestisci')) if gestione_so or gestione_servizi else None,
                ("Statistiche", "far fa-chart-bar", reverse('so:statistiche')) if gestione_so else None,
            )) if gestione_so or gestione_servizi else None
        )
    else:
        return None
