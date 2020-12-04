from anagrafica.permessi.applicazioni import (UFFICIO_SOCI, UFFICIO_SOCI_UNITA,
    DIRETTORE_CORSO, RESPONSABILE_FORMAZIONE, REFERENTE, REFERENTE_SERVIZI_SO,
    COMMISSARIO, VICE_PRESIDENTE, PRESIDENTE, )


"""
Qui vengono definiti gli incarichi.
Gli incarichi vengono risolti in modo simile ai permessi.
"""

INCARICO_PRESIDENZA = "PRES"
INCARICO_COMMISSARIO = "COM"
INCARICO_GESTIONE_SOCI = "US-GEN"
INCARICO_GESTIONE_TRASFERIMENTI = "US-TRASF"
INCARICO_GESTIONE_ESTENSIONI = "US-EST"
INCARICO_GESTIONE_FOTOTESSERE = "US-FOT"
INCARICO_GESTIONE_RISERVE = "US-RIS"
INCARICO_GESTIONE_TITOLI = "US-TIT"
INCARICO_GESTIONE_APPARTENENZE = "US-APP"
INCARICO_GESTIONE_SANGUE = "SA-SAN"
INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI = "CB-PART"
INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI = "ATT-PART"
INCARICO_GESTIONE_SO_SERVIZI_PARTECIPANTI = "SOS-PART"
INCARICO_ASPIRANTE = "ASP"


INCARICHI = (
    (INCARICO_PRESIDENZA,                       "Presidenza"),
    (INCARICO_COMMISSARIO,                      "Commissario"),
    (INCARICO_GESTIONE_SOCI,                    "Gestione dei Soci"),
    (INCARICO_GESTIONE_TRASFERIMENTI,           "Gestione dei Trasferimenti"),
    (INCARICO_GESTIONE_ESTENSIONI,              "Gestione delle Estensioni"),
    (INCARICO_GESTIONE_FOTOTESSERE,             "Gestione delle Fototessere"),
    (INCARICO_GESTIONE_TITOLI,                  "Gestione dei Titoli nella Sede"),
    (INCARICO_GESTIONE_RISERVE,                 "Gestione delle Riserve"),
    (INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI,   "Gestione dei Partecipanti all'Attività"),
    (INCARICO_GESTIONE_SO_SERVIZI_PARTECIPANTI, "Gestione dei Partecipanti al Servizio SO"),
    (INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI,  "Gestione dei Partecipanti al Corso Base"),
    (INCARICO_GESTIONE_APPARTENENZE,            "Gestione degli Appartenenti alla Sede"),
    (INCARICO_GESTIONE_SANGUE,                  "Gestione delle Donazioni Sangue"),
    (INCARICO_ASPIRANTE,                        "Autogestione Aspirante"),
)
INCARICHI_DICT = dict(INCARICHI)

INCARICHI_TIPO = (
    (INCARICO_PRESIDENZA,                       "anagrafica.Sede"),
    (INCARICO_COMMISSARIO,                      "anagrafica.Sede"),
    (INCARICO_GESTIONE_SOCI,                    "anagrafica.Sede"),
    (INCARICO_GESTIONE_TRASFERIMENTI,           "anagrafica.Sede"),
    (INCARICO_GESTIONE_ESTENSIONI,              "anagrafica.Sede"),
    (INCARICO_GESTIONE_FOTOTESSERE,             "anagrafica.Sede"),
    (INCARICO_GESTIONE_TITOLI,                  "anagrafica.Sede"),
    (INCARICO_GESTIONE_RISERVE,                 "anagrafica.Sede"),
    (INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI,   "attivita.Attivita"),
    (INCARICO_GESTIONE_SO_SERVIZI_PARTECIPANTI, "sala_operativa.ServizioSO"),
    (INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI,  "formazione.CorsoBase"),
    (INCARICO_GESTIONE_APPARTENENZE,            "anagrafica.Sede"),
    (INCARICO_GESTIONE_SANGUE,                  "anagrafica.Sede"),
    (INCARICO_ASPIRANTE,                        "anagrafica.Persona"),
)
INCARICHI_TIPO_DICT = dict(INCARICHI_TIPO)


def espandi_incarichi_ufficio_soci(qs_sede, al_giorno=None):
    return [

    ] \
        + espandi_incarichi_ufficio_soci_unita(qs_sede.espandi(), al_giorno=al_giorno)


def espandi_incarichi_ufficio_soci_unita(sede, al_giorno=None):
    return [
        (INCARICO_GESTIONE_SOCI,                        sede),
        (INCARICO_GESTIONE_APPARTENENZE,                sede),
        (INCARICO_GESTIONE_TRASFERIMENTI,               sede),
        (INCARICO_GESTIONE_ESTENSIONI,                  sede),
        (INCARICO_GESTIONE_FOTOTESSERE,                 sede),
        (INCARICO_GESTIONE_TITOLI,                      sede),
        (INCARICO_GESTIONE_RISERVE,                     sede),
    ]


def espandi_incarichi_referente_attivita(attivita, al_giorno=None):
    return [
        (INCARICO_GESTIONE_ATTIVITA_PARTECIPANTI,       attivita),
    ]

def espandi_incarichi_referente_servizio(servizio, al_giorno=None):
    return [
        (INCARICO_GESTIONE_SO_SERVIZI_PARTECIPANTI,       servizio),
    ]


def espandi_incarichi_direttore_corso(corso, al_giorno=None):
    return [
        (INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI,      corso)
    ]


def espandi_incarichi_responsabile_formazione(sede, al_giorno=None):
    from formazione.models import CorsoBase
    return [

    ] + espandi_incarichi_direttore_corso(CorsoBase.objects.filter(sede__in=sede.espandi()))


def espandi_incarichi_presidente(sede, al_giorno=None):
    return [
       (INCARICO_GESTIONE_SANGUE,                       sede),
       (INCARICO_GESTIONE_TITOLI,                       sede),
       (INCARICO_PRESIDENZA,                            sede),

    ] \
        + espandi_incarichi_ufficio_soci(sede, al_giorno=al_giorno)


def espandi_incarichi_commissario(sede, al_giorno=None):
    return [
       (INCARICO_GESTIONE_SANGUE,                       sede),
       (INCARICO_PRESIDENZA,                            sede),

    ] \
        + espandi_incarichi_ufficio_soci(sede, al_giorno=al_giorno)


# Questo dizionario contiene la corrispondenza tra la funzione di
ESPANSIONE_DELEGHE = {
    UFFICIO_SOCI_UNITA:     espandi_incarichi_ufficio_soci_unita,
    UFFICIO_SOCI:           espandi_incarichi_ufficio_soci,
    PRESIDENTE:             espandi_incarichi_presidente,
    # VICE_PRESIDENTE:        espandi_incarichi_presidente,
    COMMISSARIO:            espandi_incarichi_commissario,
    REFERENTE:              espandi_incarichi_referente_attivita,
    REFERENTE_SERVIZI_SO:   espandi_incarichi_referente_servizio,
    DIRETTORE_CORSO:        espandi_incarichi_direttore_corso,
    RESPONSABILE_FORMAZIONE:espandi_incarichi_responsabile_formazione,
}


TUTTE_CHIAVI = set(
        list(INCARICHI_DICT.keys()) +
        list(INCARICHI_TIPO_DICT.keys())
)

for incarico_chiave in TUTTE_CHIAVI:

    if incarico_chiave not in INCARICHI_DICT:
        raise ValueError("L'incarico %s non ha specificato il nome dell'incarico. Questo "
                         "puo' essere usato per mostrare messaggi agli utenti. Per favore "
                         "definisci il nome dell'incarico in anagrafica.permessi.incarichi.INCARICHI."
                         % (incarico_chiave,))

    if incarico_chiave not in INCARICHI_TIPO_DICT:
        raise ValueError("L'incarico %s non ha specificato il tipo di oggetto associato. "
                         "Associa un tipo in anagrafica.permessi.incarichi.INCARICHI_TIPO. "
                         "Ad esempio, l'incarico di gestione trasferimenti permette di gestire "
                         "i trasferimenti per una Sede CRI, quindi definisce il tipo come "
                         "'anagrafica.Sede'. Per favore definisci il tipo oggetto dell'incarico. "
                         % (incarico_chiave,))

    # if incarico_chiave not in ESPANSIONE_INCARICHI_APPROSSIMATIVA_DICT:
    #     raise ValueError("L'incarico %s non definisce un metodo reverse che suggerisca un "
    #                      "elenco di possibili oggetti Delega a partire da un oggetto "
    #                      "per il quale si ha l'incarico. Ad esempio, l'incarico di "
    #                      "gestione trasferimenti presso una unita' territoriale "
    #                      "dovrebbe ritornare l'elenco di tutte le Deleghe relative "
    #                      "a figure come Ufficio Soci e Presidente per tutto il Comitato. "
    #                      "Senza una funzione di reverse, e' impossibile inviare e-mail di "
    #                      "notifica in modo efficiente. Per favore definisci una funzione di "
    #                      "reverse e associala in anagrafica.permessi.incarichi.ESPANSIONE_INCARICHI_APPROSSIMATIVA"
    #                      % (incarico_chiave,))
