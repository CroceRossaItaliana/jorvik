from anagrafica.permessi.costanti import GESTIONE_SOCI_IIVV
from jorvik import settings


def menu_us(me):
    from django.core.urlresolvers import reverse

    from anagrafica.costanti import REGIONALE
    from anagrafica.permessi.costanti import ELENCHI_SOCI, EMISSIONE_TESSERINI, GESTIONE_SOCI, GESTIONE_SOCI_CM

    us = me and me.ha_permessi([GESTIONE_SOCI])
    uc = me and me.ha_permessi([GESTIONE_SOCI_CM])
    iv = me and me.ha_permessi([GESTIONE_SOCI_IIVV])

    return (
        ("Elenchi", (
            ("Negli elenchi", "fa-search", "/us/cerca_persona") if us else None,
            ("Volontari", "fa-list", "/us/elenchi/volontari/") if us else None,
            ("Vol. giovani", "fa-list", "/us/elenchi/giovani/") if us else None,
            ("Estesi", "fa-list", "/us/elenchi/estesi/") if us else None,
            # ("IV e CM", "fa-list", "/us/elenchi/ivcm/") if us else None,
            ("Corpo Militare", "fa-list", "/us/elenchi/cm/") if uc or us else None,
            ("Infermiere volontarie", "fa-list", "/us/elenchi/iv/") if iv or us else None,
            ("In Riserva", "fa-list", "/us/elenchi/riserva/") if us else None,
            ("Zero turni", "fa-list", "/us/elenchi/senza-turni/") if us else None,
            ("Soci", "fa-list", "/us/elenchi/soci/") if us else None,
            ("Sostenitori", "fa-list", "/us/elenchi/sostenitori/") if us else None,
            ("Ex Sostenitori", "fa-list", "/us/elenchi/ex-sostenitori/") if us else None,
            ("Dipendenti", "fa-list", "/us/elenchi/dipendenti/") if us else None,
            ("Dimessi", "fa-list", "/us/elenchi/dimessi/") if us else None,
            ("Trasferiti", "fa-list", "/us/elenchi/trasferiti/") if us else None,
            ("Ordinari", "fa-list", "/us/elenchi/ordinari/") if me and me.oggetti_permesso(ELENCHI_SOCI).filter(estensione=REGIONALE).exists() and us else None,
            ("Elettorato", "fa-list", "/us/elenchi/elettorato/") if us else None,
            ("Tesserini", "fa-list", "/us/tesserini/") if us else None,
            ("Servizio Civile Universale", "fa-list", "/us/elenchi/servizio-civile/") if us else None,
            ("Per Titoli", "fa-search", "/us/elenchi/titoli/") if us else None,
            ("Scarica elenchi richiesti", "fa-download", reverse('ufficio_soci:elenchi_richiesti_download'), '', True),
        )),
        ("Aggiungi", (
            ("Persona", "fa-plus-square", "/us/aggiungi/"),
            ("Reclama Persona", "fa-plus-square", "/us/reclama/"),
        )) if us else None,
        ("Pratiche", (
            ("Nuovo trasferimento", "fa-file-o", "/us/trasferimento/"),
            ("Nuova estensione", "fa-file-o", "/us/estensione/"),
            ("Messa in riserva", "fa-file-o", "/us/riserva/"),
            ("Nuovo provvedimento", "fa-file-o", "/us/provvedimento/"),
        )) if us else None,
        ("Quote e ricevute", (
            ("Registra Quota Associativa", "fa-plus-square", "/us/quote/nuova/"),
            ("Quote associative", "fa-money", "/us/quote/"),
            # ("Ricerca quote", "fa-search", "/us/quote/ricerca/"),
            ("Registra Ricevuta", "fa-plus-square", "/us/ricevute/nuova/"),
            ("Elenco ricevute", "fa-list", "/us/ricevute/"),
        )) if us else None,
        ("Tesserini", (
            ("Emissione", "fa-cogs", "/us/tesserini/emissione/"),
        )) if me and me.oggetti_permesso(EMISSIONE_TESSERINI).exists() and us else None,
        ("Visite mediche", (
            ("Ricerca una visita", "fa-search", "/us/ricerca-visita-medica/") if us else None,
            ("Medici del comitato", "fa-list", "/us/medici-comitato/") if us else None,
            ("Prenota una visita medica", "fa-plus-square",
             "/us/prenota-visita-medica/") if us else None,
        )) if settings.VISITE_ENABLED else None,
    )
