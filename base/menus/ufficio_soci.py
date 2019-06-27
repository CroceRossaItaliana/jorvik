def menu_us(me):
    from django.core.urlresolvers import reverse

    from anagrafica.costanti import REGIONALE
    from anagrafica.permessi.costanti import ELENCHI_SOCI, EMISSIONE_TESSERINI

    return (
        ("Elenchi", (
            ("Volontari", "fa-list", "/us/elenchi/volontari/"),
            ("Vol. giovani", "fa-list", "/us/elenchi/giovani/"),
            ("Estesi", "fa-list", "/us/elenchi/estesi/"),
            ("IV e CM", "fa-list", "/us/elenchi/ivcm/"),
            ("In Riserva", "fa-list", "/us/elenchi/riserva/"),
            ("Zero turni", "fa-list", "/us/elenchi/senza-turni/"),
            ("Soci", "fa-list", "/us/elenchi/soci/"),
            ("Sostenitori", "fa-list", "/us/elenchi/sostenitori/"),
            ("Ex Sostenitori", "fa-list", "/us/elenchi/ex-sostenitori/"),
            ("Dipendenti", "fa-list", "/us/elenchi/dipendenti/"),
            ("Dimessi", "fa-list", "/us/elenchi/dimessi/"),
            ("Trasferiti", "fa-list", "/us/elenchi/trasferiti/"),
            ("Ordinari", "fa-list", "/us/elenchi/ordinari/") if me and me.oggetti_permesso(ELENCHI_SOCI).filter(estensione=REGIONALE).exists() else None,
            ("Elettorato", "fa-list", "/us/elenchi/elettorato/"),
            ("Tesserini", "fa-list", "/us/tesserini/"),
            ("Per Titoli", "fa-search", "/us/elenchi/titoli/"),
            ("Scarica elenchi richiesti", "fa-download", reverse('elenchi_richiesti_download'), '', True),
        )),
        ("Aggiungi", (
            ("Persona", "fa-plus-square", "/us/aggiungi/"),
            ("Reclama Persona", "fa-plus-square", "/us/reclama/"),
        )),
        ("Pratiche", (
            ("Nuovo trasferimento", "fa-file-o", "/us/trasferimento/"),
            ("Nuova estensione", "fa-file-o", "/us/estensione/"),
            ("Messa in riserva", "fa-file-o", "/us/riserva/"),
            ("Nuovo provvedimento", "fa-file-o", "/us/provvedimento/"),
        )),
        ("Quote e ricevute", (
            ("Registra Quota Associativa", "fa-plus-square", "/us/quote/nuova/"),
            ("Quote associative", "fa-money", "/us/quote/"),
            # ("Ricerca quote", "fa-search", "/us/quote/ricerca/"),
            ("Registra Ricevuta", "fa-plus-square", "/us/ricevute/nuova/"),
            ("Elenco ricevute", "fa-list", "/us/ricevute/"),
        )),
        ("Tesserini", (
            ("Emissione", "fa-cogs", "/us/tesserini/emissione/"),
        )) if me and me.oggetti_permesso(EMISSIONE_TESSERINI).exists() else None,
    )
