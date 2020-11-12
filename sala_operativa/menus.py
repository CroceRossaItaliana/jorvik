from django.core.urlresolvers import reverse


def sala_operativa(me):
    from anagrafica.permessi.costanti import (GESTIONE_SERVIZI, GESTIONE_SO_SEDE, GESTIONE_OPERAZIONI, GESTIONE_FUNZIONI)

    if me and me.volontario:
        gestione_so = me.oggetti_permesso(GESTIONE_SO_SEDE).exists()
        gestione_servizi = me.oggetti_permesso(GESTIONE_SERVIZI).exists()
        gestione_operazioni = me.oggetti_permesso(GESTIONE_OPERAZIONI).exists()
        gestione_funzioni =  me.oggetti_permesso(GESTIONE_FUNZIONI).exists()

        return (
            ("Servizi", (
                ("Miei turni", "fa-list", reverse('so:storico')),
                ("Mie reperibilità", 'fa-thumb-tack', reverse('so:reperibilita')),
                ("Calendario", "fa-calendar", reverse('so:calendario')),
                ("Datore di lavore", "fa-edit", reverse('so:datore_di_lavoro')),
            )),
            ('Sala Operativa', ()) if gestione_so or gestione_servizi or gestione_operazioni else None,
            ('Operazione', (
                ("Crea Operazione", "fa-asterisk", reverse('so:organizza-operazione')) if gestione_so else None,
                ("Organizza Operazione", "fa-list", reverse('so:gestisce_operazione')) if gestione_so or gestione_operazioni else None,
            )) if gestione_so or gestione_operazioni else None,
            ('Funzione', (
                ("Crea Funzione", "fa-asterisk", reverse('so:organizza_funzione')) if gestione_so else None,
                ("Organizza Funzione", "fa-list",
                 reverse('so:gestisce_funzione')) if gestione_so or gestione_funzioni else None,
            )) if gestione_so or gestione_funzioni else None,
            ('Servizio', (
                ("Crea servizio", "fa-asterisk", reverse('so:organizza')) if gestione_so else None,
                ("Organizza Servizio", "fa-list", reverse('so:gestisci')) if gestione_so or gestione_servizi else None,
                ("Materiali e Mezzi", "fas fa-ambulance", reverse('so:mezzi')) if gestione_so else None,
            )) if gestione_so or gestione_servizi else None,
            ('', (
                ("Statistiche", "fa-bar-chart", reverse('so:statistiche')) if gestione_so else None,
            )) if gestione_so or gestione_servizi or gestione_operazioni else None,
        )
    else:
        return None
