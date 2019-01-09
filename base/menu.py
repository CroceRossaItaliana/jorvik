from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from anagrafica.costanti import REGIONALE, TERRITORIALE, LOCALE
from anagrafica.models import Sede
from anagrafica.permessi.applicazioni import DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, \
    DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, PRESIDENTE, \
    UFFICIO_SOCI, UFFICIO_SOCI_UNITA, DELEGATO_AREA, RESPONSABILE_AREA, \
    REFERENTE, RESPONSABILE_FORMAZIONE, DIRETTORE_CORSO, \
    RESPONSABILE_AUTOPARCO, DELEGATO_CO, REFERENTE_GRUPPO, RUBRICHE_TITOLI, COMMISSARIO
from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE, GESTIONE_ATTIVITA, GESTIONE_ATTIVITA_AREA, ELENCHI_SOCI, \
    GESTIONE_AREE_SEDE, GESTIONE_ATTIVITA_SEDE, EMISSIONE_TESSERINI, GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE
from .utils import remove_none
from .models import Menu

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

    deleghe_attuali = None

    if me:
        deleghe_normali = me.deleghe_attuali().exclude(tipo=PRESIDENTE)
        sedi_deleghe_normali = me.sedi_deleghe_attuali(deleghe=deleghe_normali) if me else Sede.objects.none()
        sedi_deleghe_normali = [sede.pk for sede in sedi_deleghe_normali if sede.comitati_sottostanti().exists() or sede.unita_sottostanti().exists()]
        presidente = me.deleghe_attuali(tipo=PRESIDENTE)
        sedi_deleghe_presidente = me.sedi_deleghe_attuali(deleghe=presidente).exclude(estensione__in=(TERRITORIALE,)) if me else Sede.objects.none()
        sedi_presidenti_sottostanti = [sede.pk for sede in sedi_deleghe_presidente if sede.comitati_sottostanti().exists()]
        sedi_deleghe_presidente = list(sedi_deleghe_presidente.values_list('pk', flat=True))
        sedi = sedi_deleghe_normali + sedi_deleghe_presidente
        deleghe_attuali = me.deleghe_attuali(
            oggetto_tipo=ContentType.objects.get_for_model(Sede),
            oggetto_id__in=sedi
        ).distinct().values_list('tipo', flat=True)


    gestione_corsi_sede = me.ha_permesso(GESTIONE_CORSI_SEDE) if me else False

    RUBRICA_BASE = [
        ("Referenti", "fa-book", "/utente/rubrica/referenti/"),
        ("Volontari", "fa-book", "/utente/rubrica/volontari/"),
    ]

    if deleghe_attuali:
        rubriche = []
        for slug, informazioni in RUBRICHE_TITOLI.items():
            delega, titolo, espandi = informazioni
            if titolo not in rubriche:
                rubriche.append(titolo)
                if (delega in deleghe_attuali or
                    PRESIDENTE in deleghe_attuali or
                    UFFICIO_SOCI in deleghe_attuali or
                    COMMISSARIO in deleghe_attuali
                ) and (delega != PRESIDENTE or (PRESIDENTE in deleghe_attuali and sedi_presidenti_sottostanti)):
                    RUBRICA_BASE.append(
                        (titolo, "fa-book", "".join(("/utente/rubrica/", slug, '/')))
                    )

    VOCE_RUBRICA = ("Rubrica", (
        RUBRICA_BASE
    ))

    VOCE_LINKS = ("Links", tuple((link.name, link.icon_class, link.url)
            for link in Menu.objects.filter(is_active=True).order_by('order')))

    elementi = {
        "utente": (
            (("Persona", (
                ("Benvenuto", "fa-bolt", "/utente/"),
                ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
                ("Storico", "fa-clock-o", "/utente/storico/"),
                ("Documenti", "fa-folder", "/utente/documenti/") if me and (me.volontario or me.dipendente) else None,
                ("Contatti", "fa-envelope", "/utente/contatti/"),
                ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
            )),
            ("Volontario", (
                ("Estensione", "fa-random", "/utente/estensione/"),
                ("Trasferimento", "fa-arrow-right", "/utente/trasferimento/"),
                ("Riserva", "fa-pause", "/utente/riserva/"),
            )) if me and me.volontario else None,
            VOCE_RUBRICA,
            ("Curriculum", (
                # Competenze personali commentate per non visuallizarle
                #("Competenze personali", "fa-suitcase", "/utente/curriculum/CP/"),
                ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
                ("Patenti CRI", "fa-ambulance", "/utente/curriculum/PC/") if me and (me.volontario or me.dipendente) else None,
                ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
                ("Titoli CRI", "fa-plus-square-o", "/utente/curriculum/TC/") if me and (me.volontario or me.dipendente) else None,
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
            VOCE_LINKS
        )) if me and not hasattr(me, 'aspirante') else None,
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
                ("Gruppi di lavoro", "fa-pencil", "/attivita/gruppo/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA_AREA).exists() else None,
                ("Organizza attività", "fa-asterisk", "/attivita/organizza/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA_AREA).exists() else None,
                ("Elenco attività", "fa-list", "/attivita/gestisci/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA).exists() else None,
                ("Aree di intervento", "fa-list", "/attivita/aree/") if me and me.oggetti_permesso(GESTIONE_AREE_SEDE).exists() else None,
                ("Statistiche", "fa-bar-chart", "/attivita/statistiche/") if me and me.oggetti_permesso(GESTIONE_ATTIVITA_SEDE).exists() else None,
            ))
        ) if me and me.volontario else None,
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
                ("Zero turni", "fa-list", "/us/elenchi/senza-turni/", '', True),
                ("Soci", "fa-list", "/us/elenchi/soci/"),
                ("Sostenitori", "fa-list", "/us/elenchi/sostenitori/"),
                ("Ex Sostenitori", "fa-list", "/us/elenchi/ex-sostenitori/", '', True),
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
                ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
                ("Storico", "fa-clock-o", "/utente/storico/"),
                ("Contatti", "fa-envelope", "/utente/contatti/"),
                ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
                ("Competenze personali", "fa-suitcase", "/utente/curriculum/CP/"),
                ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
                ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
            )),
            ("Nelle vicinanze", (
                ("Impostazioni", "fa-gears", "/aspirante/impostazioni/"),
                ("Corsi Base", "fa-list", "/aspirante/corsi-base/"),
                ("Sedi CRI", "fa-list", "/aspirante/sedi/"),
            )),
            ("Sicurezza", (
                ("Cambia password", "fa-key", "/utente/cambia-password/"),
                ("Impostazioni Privacy", "fa-cogs", "/utente/privacy/"),
            ),
            ),
        ) if me and hasattr(me, 'aspirante') else (
            ("Gestione Corsi", (
                ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
            )),
        ),
    }
    if me and hasattr(me, 'aspirante'):
        elementi['elementi_anagrafica'] = elementi['aspirante']
    else:
        elementi['elementi_anagrafica'] = elementi['utente']
    return remove_none(elementi)
