__author__ = 'alfioemanuele'

"""
Questa pagina contiene i vari menu che vengono mostrati nella barra laterale dei template.
La costante MENU e' accessibile attraverso "menu" nei template.
"""

MENU = {
    "utente": (
        ("Volontario", (
            ("Benvenuto", "fa-bolt", "/utente/"),
            ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
            ("Storico", "fa-clock-o", "/utente/storico/"),
            ("Documenti", "fa-folder", "/utente/documenti/"),
            ("Contatti", "fa-envelope", "/utente/contatti/"),
            ("Estensione", "fa-arrow-right", "/utente/estensione/"),
        )),
        ("Sicurezza", (
            ("Cambia password", "fa-key", "/utente/cambia-password/"),
        )),
    ),
    "posta": (
        ("Posta", (
            ("In arrivo", "fa-inbox", "/posta/in-arrivo/"),
            ("In uscita", "fa-mail-forward", "/posta/in-uscita/"),
        )),
    ),
    "attivita": (
        ("Attività", (
            ("Calendario", "fa-calendar", "/attivita/calendario/"),
            ("Miei turni", "fa-list", "/attivita/storico/"),
            ("Gruppi", "fa-users", "/attivita/gruppi/"),
            ("Reperibilità", "fa-thumb-tack", "/attivita/reperibilita/"),
        )),
    ),
    "autorizzazioni": (
        ("Richieste", (
            ("In attesa", "fa-user-plus", "/autorizzazioni/"),
            ("Storico", "fa-clock-o", "/autorizzazioni/storico/"),
        )),
    ),
    "us": (
        ("Elenchi", (
            ("Soci", "fa-list", "/us/elenco/soci/"),
            ("Sostenitori", "fa-list", "/us/elenco/sostenitori/"),
            ("Elettorato", "fa-list", "/us/elenco/elettorato/"),
        )),
        ("Aggiungi", (
            ("Volontario", "fa-plus-square", "/us/aggiungi/volontario/"),
            ("Sostenitore", "fa-plus-square", "/us/aggiungi/sostenitore/"),
        )),
        ("Pratiche", (
            ("Nuovo trasferimento", "fa-file-o", "/us/trasferimento/"),
            ("Nuova estensione", "fa-file-o", "/us/estensione/"),
            ("Messa in riserva", "fa-file-o", "/us/riserva/"),
            ("Nuovo provvedimento", "fa-file-o", "/us/provvedimento/"),
        )),
        ("Quote", (
            ("Quote associative", "fa-money", "/us/trasferimento/"),
            ("Ricerca", "fa-search", "/us/estensione/"),
        )),
        ("Tesserini", (
            ("Non riconsegnati", "fa-credit-card", "/us/non-riconsegnati/"),
        )),
    ),

}