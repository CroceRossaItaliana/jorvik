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
        )),
        ("Sicurezza", (
            ("Cambia password", "fa-key", "/utente/cambia-password/"),
            ("Storico accesso", "fa-list", "/utente/storico-accessi/"),
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
            ("Calendario", "fa-calendar", "/attivita/"),
            ("Miei turni", "fa-list", "/attivita/storico/"),
            ("Gruppi", "fa-users", "/attivita/gruppi/"),
            ("Reperibilità", "fa-thumb-tack", "/attivita/reperibilita/"),
        )),
    )
}