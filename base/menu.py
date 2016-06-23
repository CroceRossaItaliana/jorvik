from anagrafica.costanti import REGIONALE
from anagrafica.permessi.applicazioni import DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, \
    DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, PRESIDENTE, \
    UFFICIO_SOCI, UFFICIO_SOCI_UNITA, DELEGATO_AREA, RESPONSABILE_AREA, \
    REFERENTE, RESPONSABILE_FORMAZIONE, DIRETTORE_CORSO, \
    RESPONSABILE_AUTOPARCO, DELEGATO_CO, REFERENTE_GRUPPO
from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE, GESTIONE_ATTIVITA, GESTIONE_ATTIVITA_AREA, ELENCHI_SOCI, \
    GESTIONE_AREE_SEDE, GESTIONE_ATTIVITA_SEDE, EMISSIONE_TESSERINI, GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE
from base.utils import remove_none

__author__ = 'alfioemanuele'

"""
Questa pagina contiene i vari menu che vengono mostrati nella barra laterale dei template.
La costante MENU e' accessibile attraverso "menu" nei template.
"""


def menu(request):
    """
    Ottiene il menu per una data richiesta.
    """
    from base.viste import ORDINE_ASCENDENTE, ORDINE_DISCENDENTE, ORDINE_DEFAULT

    me = request.me if hasattr(request, 'me') else None

    deleghe_attuali = me.deleghe_attuali() if me else None

    delegato_giovani = deleghe_attuali.filter(tipo=DELEGATO_OBIETTIVO_5).count() if deleghe_attuali else 0

    presidente = False
    ufficio_soci = False
    ufficio_soci_unita = False
    delega_area = False
    delega_obiettivo_1 = False
    delega_obiettivo_2 = False
    delega_obiettivo_3 = False
    delega_obiettivo_4 = False
    delega_obiettivo_6 = False
    responsabile_area = False
    referente_attivita = False
    referente_gruppo = False
    centrale_operativa = False
    responsabile_formazione = False
    direttore_corso = False
    responsabile_autoparco = False

    if me:
        delegato_giovani = delegato_giovani > 0
    else:
        giovane_e_delegato_giovani = False

    ha_deleghe = deleghe_attuali.exists() if deleghe_attuali else False

    if ha_deleghe:
        presidente = deleghe_attuali.filter(tipo=PRESIDENTE).exists()
        ufficio_soci = deleghe_attuali.filter(tipo=UFFICIO_SOCI).exists()
        ufficio_soci_unita = deleghe_attuali.filter(tipo=UFFICIO_SOCI_UNITA).exists()
        delega_area = deleghe_attuali.filter(tipo=DELEGATO_AREA).exists()
        delega_obiettivo_1 = deleghe_attuali.filter(tipo=DELEGATO_OBIETTIVO_1).exists()
        delega_obiettivo_2 = deleghe_attuali.filter(tipo=DELEGATO_OBIETTIVO_2).exists()
        delega_obiettivo_3 = deleghe_attuali.filter(tipo=DELEGATO_OBIETTIVO_3).exists()
        delega_obiettivo_4 = deleghe_attuali.filter(tipo=DELEGATO_OBIETTIVO_4).exists()
        delega_obiettivo_6 = deleghe_attuali.filter(tipo=DELEGATO_OBIETTIVO_6).exists()
        responsabile_area = deleghe_attuali.filter(tipo=RESPONSABILE_AREA).exists()
        referente_attivita = deleghe_attuali.filter(tipo=REFERENTE).exists()
        referente_gruppo = deleghe_attuali.filter(tipo=REFERENTE_GRUPPO).exists()
        centrale_operativa = deleghe_attuali.filter(tipo=DELEGATO_CO).exists()
        responsabile_formazione = deleghe_attuali.filter(tipo=RESPONSABILE_FORMAZIONE).exists()
        direttore_corso = deleghe_attuali.filter(tipo=DIRETTORE_CORSO).exists()
        responsabile_autoparco = deleghe_attuali.filter(tipo=RESPONSABILE_AUTOPARCO).exists()

    gestione_corsi_sede = me.ha_permesso(GESTIONE_CORSI_SEDE) if me else False

    return remove_none({
        "utente": (
            (("Persona", (
                ("Benvenuto", "fa-bolt", "/utente/"),
                ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
                ("Storico", "fa-clock-o", "/utente/storico/"),
                ("Documenti", "fa-folder", "/utente/documenti/"),
                ("Contatti", "fa-envelope", "/utente/contatti/"),
                ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
            )),
            ("Volontario", (
                ("Estensione", "fa-random", "/utente/estensione/"),
                ("Trasferimento", "fa-arrow-right", "/utente/trasferimento/"),
                ("Riserva", "fa-pause", "/utente/riserva/"),
            )) ,
            ("Rubrica", (
                ("Referenti", "fa-book", "/utente/rubrica/referenti/"),
                ("Volontari", "fa-book", "/utente/rubrica/volontari/"),
                ("Presidenti", "fa-book", "/utente/rubrica/presidenti/") if ha_deleghe and presidente else None,
                ("Delegati Ufficio Soci", "fa-book", "/utente/rubrica/delegati_us/") if ha_deleghe and ufficio_soci else None,
                ("Delegati Ufficio Soci Unità Territoriale", "fa-book", "/utente/rubrica/delegati_us_unita/") if ha_deleghe and ufficio_soci_unita else None,
                ("Delegati d'Area", "fa-book", "/utente/rubrica/delegati_area/") if ha_deleghe and delega_area else None,
                ("Delegati Obiettivo I (Salute)", "fa-book", "/utente/rubrica/delegati_obiettivo_1/") if ha_deleghe and delega_obiettivo_1 else None,
                ("Delegati Obiettivo II (Sociale)", "fa-book", "/utente/rubrica/delegati_obiettivo_2/") if ha_deleghe and delega_obiettivo_2 else None,
                ("Delegati Obiettivo III (Emergenze)", "fa-book", "/utente/rubrica/delegati_obiettivo_3/") if ha_deleghe and delega_obiettivo_3 else None,
                ("Delegati Obiettivo IV (Emergenze)", "fa-book", "/utente/rubrica/delegati_obiettivo_4/") if ha_deleghe and delega_obiettivo_4 else None,
                ("Delegati Obiettivo VI (Emergenze)", "fa-book", "/utente/rubrica/delegati_obiettivo_6/") if ha_deleghe and delega_obiettivo_6 else None,
                ("Responsabili d'Area", "fa-book", "/utente/rubrica/responsabili_area/") if ha_deleghe and responsabile_area else None,
                ("Referenti Attività", "fa-book", "/utente/rubrica/referenti_attivita/") if ha_deleghe and referente_attivita else None,
                ("Referenti Gruppi", "fa-book", "/utente/rubrica/referenti_gruppi/") if ha_deleghe and referente_gruppo else None,
                ("Delegati Centrale operativa", "fa-book", "/utente/rubrica/centrali_operative/") if ha_deleghe and centrale_operativa else None,
                ("Responsabili Formazione", "fa-book", "/utente/rubrica/responsabili_formazione/") if ha_deleghe and responsabile_formazione else None,
                ("Direttori Corsi", "fa-book", "/utente/rubrica/direttori_corsi/") if ha_deleghe and direttore_corso else None,
                ("Responsabili autoparco", "fa-book", "/utente/rubrica/responsabili_autoparco/") if ha_deleghe and responsabile_autoparco else None,
                ("Giovani", "fa-book", "/utente/rubrica/giovani/") if delegato_giovani else None,
            )) ,
            ("Curriculum", (
                ("Competenze personali", "fa-suitcase", "/utente/curriculum/CP/"),
                ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
                ("Patenti CRI", "fa-ambulance", "/utente/curriculum/PC/"),
                ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
                ("Titoli CRI", "fa-plus-square-o", "/utente/curriculum/TC/"),
            )),
            ("Donatore", (
                ("Profilo Donatore", "fa-user", "/utente/donazioni/profilo/"),
                ("Donazioni di Sangue", "fa-flask", "/utente/donazioni/sangue/")
                    if hasattr(me, 'donatore') else None,
            )) if me and me.volontario else None,
            ("Sicurezza", (
                ("Cambia password", "fa-key", "/utente/cambia-password/"),
                ("Impostazioni Privacy", "fa-cogs", "/utente/privacy/"),
            )),
        )),
        "posta": (
            ("Posta", (
                ("Scrivi", "fa-pencil", "/posta/scrivi/"),
                ("In arrivo", "fa-inbox", "/posta/in-arrivo/"),
                ("In uscita", "fa-mail-forward", "/posta/in-uscita/"),
            )),
        ),
        "veicoli": (
            ("Veicoli", (
                ("Dashboard", "fa-gears", "/veicoli/"),
                ("Veicoli", "fa-car", "/veicoli/elenco/"),
                ("Autoparchi", "fa-dashboard", "/veicoli/autoparchi/"),
            )),
        ),
        "attivita": (
            ("Attività", (
                ("Calendario", "fa-calendar", "/attivita/calendario/"),
                ("Miei turni", "fa-list", "/attivita/storico/"),
                ("Gruppi di lavoro", "fa-users", "/attivita/gruppi/"),
                ("Reperibilità", "fa-thumb-tack", "/attivita/reperibilita/"),
            )),
            ("Gestione", (
                ("Organizza attività", "fa-asterisk", "/attivita/organizza/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA_AREA).exists() else None,
                ("Elenco attività", "fa-list", "/attivita/gestisci/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA).exists() else None,
                ("Aree di intervento", "fa-list", "/attivita/aree/") if me and me.oggetti_permesso(GESTIONE_AREE_SEDE).exists() else None,
                ("Statistiche", "fa-bar-chart", "/attivita/statistiche/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE).exists() else None,
            ))
        ),
        "autorizzazioni": (
            ("Richieste", (
                ("In attesa", "fa-user-plus", "/autorizzazioni/"),
                ("Storico", "fa-clock-o", "/autorizzazioni/storico/"),
            )),
            ("Ordina", (
                ("Dalla più recente", "fa-sort-numeric-desc", "?ordine=DESC",
                 request.GET.get('ordine', default="DESC") == "DESC"),
                ("Dalla più vecchia", "fa-sort-numeric-asc", "?ordine=ASC",
                 request.GET.get('ordine', default="DESC") == "ASC"),
            )),
        ),
        "presidente": (
            ("Sedi CRI", (
                ("Elenco", "fa-list", "/presidente/"),
            )),
        ),
        "us": (
            ("Elenchi", (
                ("Volontari", "fa-list", "/us/elenchi/volontari/"),
                ("Vol. giovani", "fa-list", "/us/elenchi/giovani/"),
                ("Estesi", "fa-list", "/us/elenchi/estesi/"),
                ("IV e CM", "fa-list", "/us/elenchi/ivcm/"),
                ("In Riserva", "fa-list", "/us/elenchi/riserva/"),
                ("Soci", "fa-list", "/us/elenchi/soci/"),
                ("Sostenitori", "fa-list", "/us/elenchi/sostenitori/"),
                ("Dipendenti", "fa-list", "/us/elenchi/dipendenti/"),
                ("Dimessi", "fa-list", "/us/elenchi/dimessi/"),
                ("Trasferiti", "fa-list", "/us/elenchi/trasferiti/"),
                ("Ordinari", "fa-list", "/us/elenchi/ordinari/") if me and me.oggetti_permesso(ELENCHI_SOCI).filter(estensione=REGIONALE).exists() else None,
                ("Elettorato", "fa-list", "/us/elenchi/elettorato/"),
                ("Tesserini", "fa-list", "/us/tesserini/"),
                ("Per Titoli", "fa-search", "/us/elenchi/titoli/"),
            )),
            ("Aggiungi", (
                ("Persona", "fa-plus-square", "/us/aggiungi/"),
                ("Reclama Persona", "fa-plus-square", "/us/reclama/"),            )),
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
        ),
        "co": (
            ("Centrale Operativa", (
                ("Reperibilità", "fa-clock-o", "/centrale-operativa/reperibilita/"),
                ("Turni", "fa-calendar", "/centrale-operativa/turni/"),
                ("Poteri", "fa-magic", "/centrale-operativa/poteri/")
                if me and me.oggetti_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE).exists() else None,
            )),
        ),
        "formazione": (
            ("Corsi Base", (
                ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
                ("Domanda formativa", "fa-area-chart", "/formazione/corsi-base/domanda/")
                    if gestione_corsi_sede else None,
                ("Pianifica nuovo", "fa-asterisk", "/formazione/corsi-base/nuovo/")
                    if gestione_corsi_sede else None,
            )),
            ("Corsi di Formazione", (
                ("Elenco Corsi di Formazione", "fa-list", "/formazione/corsi-formazione/"),
                ("Pianifica nuovo", "fa-asterisk", "/formazione/corsi-formazione/nuovo/"),
            )) if False else None,
        ),
        "aspirante": (
            ("Aspirante", (
                ("Home page", "fa-home", "/aspirante/"),
                ("Impostazioni", "fa-gears", "/aspirante/impostazioni/")
            )),
            ("Nelle vicinanze", (
                ("Corsi Base", "fa-list", "/aspirante/corsi-base/"),
                ("Sedi CRI", "fa-list", "/aspirante/sedi/"),
            )),
        ) if me and hasattr(me, 'aspirante') else (
            ("Gestione Corsi", (
                ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
            )),
        ),
    })
