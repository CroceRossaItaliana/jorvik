from datetime import date

from django.db.models import Q

from anagrafica.permessi.costanti import (GESTIONE_SOCI, ELENCHI_SOCI,
                                          GESTIONE_ATTIVITA_SEDE,
                                          GESTIONE_CORSI_SEDE, GESTIONE_SEDE,
                                          GESTIONE_ATTIVITA_AREA,
                                          GESTIONE_ATTIVITA,
                                          GESTIONE_CORSO, MODIFICA, LETTURA,
                                          COMPLETO, GESTIONE_AUTOPARCHI_SEDE,
                                          GESTIONE_GRUPPO, GESTIONE_GRUPPI,
                                          GESTIONE_GRUPPI_SEDE, GESTIONE,
                                          GESTIONE_AREE_SEDE,
                                          GESTIONE_REFERENTI_ATTIVITA,
                                          GESTIONE_SO_SEDE,
                                          GESTIONE_CENTRALE_OPERATIVA_SEDE,
                                          EMISSIONE_TESSERINI,
                                          GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE,
                                          RUBRICA_UFFICIO_SOCI,
                                          RUBRICA_UFFICIO_SOCI_UNITA,
                                          RUBRICA_PRESIDENTI,
                                          RUBRICA_DELEGATI_AREA,
                                          RUBRICA_DELEGATI_OBIETTIVO_1,
                                          RUBRICA_DELEGATI_OBIETTIVO_2,
                                          RUBRICA_DELEGATI_OBIETTIVO_3,
                                          RUBRICA_DELEGATI_OBIETTIVO_4,
                                          RUBRICA_DELEGATI_OBIETTIVO_6,
                                          RUBRICA_DELEGATI_GIOVANI,
                                          RUBRICA_RESPONSABILI_AREA,
                                          RUBRICA_REFERENTI_ATTIVITA,
                                          RUBRICA_REFERENTI_SO,
                                          RUBRICA_REFERENTI_GRUPPI,
                                          RUBRICA_CENTRALI_OPERATIVE,
                                          RUBRICA_RESPONSABILI_FORMAZIONE,
                                          RUBRICA_DIRETTORI_CORSI,
                                          RUBRICA_RESPONSABILI_AUTOPARCO,
                                          RUBRICA_COMMISSARI,
                                          RUBRICA_CONSIGLIERE_GIOVANE,
                                          RUBRICA_SALE_OPERATIVE,
                                          GESTIONE_SERVIZI,
                                          GESTIONE_REFERENTI_SO,
                                          GESTIONE_SOCI_CM,
                                          GESTIONE_SOCI_IIVV, GESTIONE_OPERAZIONI, GESTIONE_REFERENTI_OPERAZIONI_SO,
                                          GESTIONE_FUNZIONI, GESTIONE_REFERENTI_FUNZIONI_SO, GESTIONE_EVENTO,
                                          GESTIONE_EVENTI_SEDE, )

"""            Questo file gestisce la espansione dei permessi in Gaia.
 ===============================================================================
 |                                    ! HEEEEY, TU !                           |
 ===============================================================================
  Prima di avventurarti da queste parti, assicurati di leggere la documentazione:
  https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ===============================================================================
"""


def espandi_persona(persona, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione, Riserva
    from ufficio_soci.models import Quota, Tesserino
    try:
        """
        Punto 3: https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso#creare-una-nuova-delega-ie-ruolo

        [Permesso, QuerySet]
        * Il Permesso è una costante tra i permessi dichiarati in anagrafica/permessi/costanti.py
        * QuerySet è l'elenco degli oggetti sui quali è valido il permesso.

          Il tipo di modello del QuerySet deve essere concorde da quello aspettato dal Permesso,
          specificato e verificabile in PERMESSI_OGGETTI all'interno di anagrafica/permessi/costanti.py
        """
        return [
            (LETTURA, Trasferimento.objects.filter(persona=persona)),
            (LETTURA, Estensione.objects.filter(persona=persona)),
            (LETTURA, Riserva.objects.filter(persona=persona)),
            (LETTURA, Quota.objects.filter(persona=persona)),
            (LETTURA, Tesserino.objects.filter(persona=persona)),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_gestione_soci(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione, Riserva
    from ufficio_soci.models import Quota, Tesserino
    try:
        return [
            (MODIFICA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                         membro__in=Appartenenza.MEMBRO_DIRETTO).via(
                "appartenenze"))),
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                        membro__in=Appartenenza.MEMBRO_ESTESO).via(
                "appartenenze"))),
            (MODIFICA, Trasferimento.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                               membro__in=Appartenenza.MEMBRO_DIRETTO).via(
                "persona__appartenenze"))),
            (LETTURA, Trasferimento.objects.filter(destinazione__in=qs_sedi)),
            (MODIFICA, Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                            membro__in=Appartenenza.MEMBRO_DIRETTO).via(
                "persona__appartenenze"))),
            (LETTURA, Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                           membro__in=Appartenenza.MEMBRO_ESTESO).via(
                "persona__appartenenze"))),
            (LETTURA, Estensione.objects.filter(destinazione__in=qs_sedi)),
            (MODIFICA, Quota.objects.filter(sede__in=qs_sedi)),
            (LETTURA, Riserva.objects.filter(appartenenza__sede__in=qs_sedi)),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_gestione_soci_cm(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza
    
    try:
        return [
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                        membro__in=Appartenenza.MEMBRO_ESTESO).via(
                "appartenenze"))),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_gestione_soci_iivv(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza

    try:
        return [
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi,
                                                                        membro__in=Appartenenza.MEMBRO_ESTESO).via(
                "appartenenze"))),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_emissione_tesserini(qs_sedi, al_giorno=None):
    from ufficio_soci.models import Quota, Tesserino
    try:
        return [
            (MODIFICA, Tesserino.objects.filter(emesso_da__in=qs_sedi)),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_elenchi_soci(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza, Sede, Riserva
    from ufficio_soci.models import Quota, Tesserino
    try:
        return [
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi).via("appartenenze"))),
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze"))),
            (LETTURA, Quota.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze"))),
            (LETTURA, Quota.objects.filter(Q(Q(sede__in=qs_sedi) | Q(appartenenza__sede__in=qs_sedi)))),
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, confermata=True, ritirata=False).via("appartenenze"))),
            (LETTURA, Persona.objects.filter(Appartenenza.con_esito_pending(sede__in=qs_sedi).via("appartenenze"))),
            (LETTURA, Persona.objects.filter(Appartenenza.con_esito_no(sede__in=qs_sedi).via("appartenenze"))),
            (LETTURA, Riserva.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, confermata=True, ritirata=False).via("persona__appartenenze"))),
            (LETTURA, Tesserino.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, confermata=True, ritirata=False).via("persona__appartenenze"))),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_rubriche(qs_sedi, al_giorno=date.today()):
    try:
        return [
            (LETTURA, qs_sedi),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_rubrica_consigliere_giovane(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_ufficio_soci(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_ufficio_soci_unita(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_presidenti(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_commissari(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_area(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_obiettivo_1(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_obiettivo_2(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_obiettivo_3(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_obiettivo_4(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_obiettivo_6(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_delegati_giovani(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_responsabili_area(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_referenti_attivita(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_referenti_so(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_referenti_gruppi(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_centrali_operative(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_sale_operative(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_responsabili_formazione(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_direttori_corsi(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_rubrica_responsabili_autoparco(qs_sedi, al_giorno=date.today()):
    return espandi_rubriche(qs_sedi, al_giorno)


def espandi_gestione_sede(qs_sedi, al_giorno=None):
    try:
        return [
            (GESTIONE, qs_sedi),
        ]
    except (AttributeError, ValueError, KeyError):
        return []


def espandi_gestione_attivita_sede(qs_sedi, al_giorno=None):
    from attivita.models import Attivita
    try:
        return [
                   (COMPLETO, Attivita.objects.filter(sede__in=qs_sedi.espandi())),
               ] \
               + espandi_gestione_attivita(Attivita.objects.filter(sede__in=qs_sedi.espandi()))
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_aree_sede(qs_sedi, al_giorno=None):
    from attivita.models import Area
    try:
        return [
            (COMPLETO, Area.objects.filter(sede__in=qs_sedi)),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_attivita_area(qs_aree, al_giorno=None):
    from attivita.models import Attivita
    try:
        return [
                   (COMPLETO, Attivita.objects.filter(area__in=qs_aree)),
               ] \
               + espandi_gestione_attivita(Attivita.objects.filter(area__in=qs_aree))
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_attivita(qs_attivita, al_giorno=None):
    from anagrafica.models import Persona
    try:
        return [
            (MODIFICA, qs_attivita),
            (LETTURA, Persona.objects.filter(partecipazioni__turno__attivita__in=qs_attivita))
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_centrale_operativa_sede(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza
    try:
        return [
            (LETTURA, Persona.objects.filter(
                Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi).via("appartenenze"),
                reperibilita__isnull=False)),
            (LETTURA, Persona.objects.filter(
                Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi).via("appartenenze"),
                coturni__isnull=False)),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_poteri_centrale_operativa_sede(qs_sedi, al_giorno=None):
    return [
    ]


def espandi_gestione_referenti_attivita(qs_attivita, al_giorno=None):
    return [
    ]


def espandi_gestione_autoparchi_sede(qs_sedi, al_giorno=None):
    from veicoli.models import Autoparco, Veicolo, Collocazione
    try:
        return [
            (MODIFICA, Autoparco.objects.filter(sede__in=qs_sedi.espandi())),
            (MODIFICA, Veicolo.objects.filter(Collocazione.query_attuale().via("collocazioni"),
                                              collocazioni__autoparco__sede__in=qs_sedi.espandi())),
            (MODIFICA, Collocazione.query_attuale(autoparco__sede__in=qs_sedi.espandi())),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_corsi_sede(qs_sedi, al_giorno=None):
    from formazione.models import CorsoBase
    try:
        return [
                   (COMPLETO, CorsoBase.objects.filter(sede__in=qs_sedi)),
               ] \
               + espandi_gestione_corso(CorsoBase.objects.filter(sede__in=qs_sedi))
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_corso(qs_corsi, al_giorno=None):
    from anagrafica.models import Persona
    from formazione.models import PartecipazioneCorsoBase

    try:
        return [
            (MODIFICA, qs_corsi),
            (MODIFICA,
             Persona.objects.filter(partecipazioni_corsi__corso__in=qs_corsi).exclude(aspirante__id__isnull=True)),
            (MODIFICA, PartecipazioneCorsoBase.objects.filter(corso__in=qs_corsi)),
            (LETTURA, Persona.objects.filter(partecipazioni_corsi__corso__in=qs_corsi)),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_eventi_sede(qs_sedi, al_giorno=None):
    from formazione.models import Evento
    try:
        return [
                   (COMPLETO, Evento.objects.filter(sede__in=qs_sedi)),
               ] \
               + espandi_gestione_evento(Evento.objects.filter(sede__in=qs_sedi))
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_evento(qs_eventi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza

    try:
        return [
            (GESTIONE, qs_eventi),
            (MODIFICA, Persona.objects.filter(
                Appartenenza.query_attuale(membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))
             ),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_gruppo(qs_gruppi, al_giorno=None):
    from anagrafica.models import Persona
    from gruppi.models import Appartenenza
    try:
        return [
            (MODIFICA, qs_gruppi),
            (LETTURA, Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno).via("appartenenze_gruppi"),
                                             appartenenze_gruppi__gruppo__in=qs_gruppi)),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_gruppi(qs_gruppi, al_giorno=None):
    try:
        return [
            (MODIFICA, qs_gruppi),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_gruppi_sede(qs_sedi, al_giorno=None):
    from gruppi.models import Gruppo
    try:
        return [

               ] + espandi_gestione_gruppo(Gruppo.objects.filter(sede__in=qs_sedi), al_giorno=al_giorno)
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_so_sede(qs_servizi, al_giorno=None):
    from sala_operativa.models import ServizioSO
    try:
        return [
            (COMPLETO, ServizioSO.objects.filter(sede__in=qs_servizi.espandi())),
        ] \
        + espandi_gestione_servizi(ServizioSO.objects.filter(sede__in=qs_servizi.espandi(pubblici=True)))
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_referenti_so(qs_servizi, al_giorno=None):
    return [
    ]


def espandi_gestione_servizi(qs_servizi, al_giorno=None):
    from anagrafica.models import Persona
    from sala_operativa.models import ReperibilitaSO

    persone = ReperibilitaSO.objects.filter(partecipazioneso__turno__attivita__in=qs_servizi).values_list('persona', flat=True)

    try:
        return [
            (MODIFICA, qs_servizi),
            (LETTURA, Persona.objects.filter(pk__in=persone)),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_operazioni(qs_operazioni, al_giorno=None):

    try:
        return [
            (MODIFICA, qs_operazioni),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


def espandi_gestione_funzioni(qs_funzioni, al_giorno=None):

    try:
        return [
            (MODIFICA, qs_funzioni),
        ]
    except (AttributeError, ValueError, KeyError, TypeError):
        return []


ESPANDI_PERMESSI = {
    # SOCI
    GESTIONE_SOCI: espandi_gestione_soci,
    GESTIONE_SOCI_CM: espandi_gestione_soci_cm,
    GESTIONE_SOCI_IIVV: espandi_gestione_soci_iivv,
    ELENCHI_SOCI: espandi_elenchi_soci,
    EMISSIONE_TESSERINI: espandi_emissione_tesserini,

    # ANAGRAFICA
    GESTIONE_SEDE: espandi_gestione_sede,
    GESTIONE_AREE_SEDE: espandi_gestione_aree_sede,

    # ATTIVITA
    GESTIONE_ATTIVITA_SEDE: espandi_gestione_attivita_sede,
    GESTIONE_ATTIVITA_AREA: espandi_gestione_attivita_area,
    GESTIONE_REFERENTI_ATTIVITA: espandi_gestione_referenti_attivita,
    GESTIONE_ATTIVITA: espandi_gestione_attivita,

    # SO
    GESTIONE_SO_SEDE: espandi_gestione_so_sede,
    GESTIONE_REFERENTI_SO: espandi_gestione_referenti_so,
    GESTIONE_REFERENTI_OPERAZIONI_SO: espandi_gestione_referenti_so,
    GESTIONE_REFERENTI_FUNZIONI_SO: espandi_gestione_referenti_so,
    GESTIONE_SERVIZI: espandi_gestione_servizi,
    GESTIONE_OPERAZIONI: espandi_gestione_operazioni,
    GESTIONE_FUNZIONI: espandi_gestione_operazioni,

    # FORMAZIONE
    GESTIONE_CORSI_SEDE: espandi_gestione_corsi_sede,
    GESTIONE_CORSO: espandi_gestione_corso,
    GESTIONE_EVENTO: espandi_gestione_evento,
    GESTIONE_EVENTI_SEDE: espandi_gestione_corsi_sede,
    GESTIONE_AUTOPARCHI_SEDE: espandi_gestione_autoparchi_sede,

    # GRUPPI
    GESTIONE_GRUPPO: espandi_gestione_gruppo,
    GESTIONE_GRUPPI: espandi_gestione_gruppi,
    GESTIONE_GRUPPI_SEDE: espandi_gestione_gruppi_sede,

    # CO
    GESTIONE_CENTRALE_OPERATIVA_SEDE: espandi_gestione_centrale_operativa_sede,
    GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE: espandi_gestione_poteri_centrale_operativa_sede,

    # RUBRICA
    RUBRICA_UFFICIO_SOCI: espandi_rubrica_ufficio_soci,
    RUBRICA_UFFICIO_SOCI_UNITA: espandi_rubrica_ufficio_soci_unita,
    RUBRICA_PRESIDENTI: espandi_rubrica_presidenti,
    RUBRICA_COMMISSARI: espandi_rubrica_commissari,
    RUBRICA_CONSIGLIERE_GIOVANE: espandi_rubrica_consigliere_giovane,
    RUBRICA_DELEGATI_AREA: espandi_rubrica_delegati_area,
    RUBRICA_DELEGATI_OBIETTIVO_1: espandi_rubrica_delegati_obiettivo_1,
    RUBRICA_DELEGATI_OBIETTIVO_2: espandi_rubrica_delegati_obiettivo_2,
    RUBRICA_DELEGATI_OBIETTIVO_3: espandi_rubrica_delegati_obiettivo_3,
    RUBRICA_DELEGATI_OBIETTIVO_4: espandi_rubrica_delegati_obiettivo_4,
    RUBRICA_DELEGATI_OBIETTIVO_6: espandi_rubrica_delegati_obiettivo_6,
    RUBRICA_DELEGATI_GIOVANI: espandi_rubrica_delegati_giovani,
    RUBRICA_RESPONSABILI_AREA: espandi_rubrica_responsabili_area,
    RUBRICA_REFERENTI_ATTIVITA: espandi_rubrica_referenti_attivita,
    RUBRICA_REFERENTI_SO: espandi_rubrica_referenti_so,
    RUBRICA_REFERENTI_GRUPPI: espandi_rubrica_referenti_gruppi,
    RUBRICA_CENTRALI_OPERATIVE: espandi_rubrica_centrali_operative,
    RUBRICA_SALE_OPERATIVE: espandi_rubrica_sale_operative,
    RUBRICA_RESPONSABILI_FORMAZIONE: espandi_rubrica_responsabili_formazione,
    RUBRICA_DIRETTORI_CORSI: espandi_rubrica_direttori_corsi,
    RUBRICA_RESPONSABILI_AUTOPARCO: espandi_rubrica_responsabili_autoparco,
}
