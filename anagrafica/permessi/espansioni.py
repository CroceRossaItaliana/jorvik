from datetime import date

from django.db.models import Q

__author__ = 'alfioemanuele'

from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI, GESTIONE_ATTIVITA_SEDE, GESTIONE_CORSI_SEDE, \
    GESTIONE_SEDE, GESTIONE_ATTIVITA_AREA, GESTIONE_ATTIVITA, GESTIONE_CORSO, MODIFICA, LETTURA, COMPLETO, \
    GESTIONE_AUTOPARCHI_SEDE, GESTIONE_GRUPPO, GESTIONE_GRUPPI_SEDE, GESTIONE, GESTIONE_AREE_SEDE, \
    GESTIONE_REFERENTI_ATTIVITA, GESTIONE_CENTRALE_OPERATIVA_SEDE, EMISSIONE_TESSERINI, \
    GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE, RUBRICA_UFFICIO_SOCI, RUBRICA_UFFICIO_SOCI_UNITA, \
    RUBRICA_PRESIDENTI, RUBRICA_DELEGATI_AREA, RUBRICA_DELEGATI_OBIETTIVO_1, RUBRICA_DELEGATI_OBIETTIVO_2, \
    RUBRICA_DELEGATI_OBIETTIVO_3, RUBRICA_DELEGATI_OBIETTIVO_4, RUBRICA_DELEGATI_OBIETTIVO_6, \
    RUBRICA_DELEGATI_GIOVANI, RUBRICA_RESPONSABILI_AREA, RUBRICA_REFERENTI_ATTIVITA, \
    RUBRICA_REFERENTI_GRUPPI, RUBRICA_CENTRALI_OPERATIVE, RUBRICA_RESPONSABILI_FORMAZIONE, \
    RUBRICA_DIRETTORI_CORSI, RUBRICA_RESPONSABILI_AUTOPARCO

"""
Questo file gestisce la espansione dei permessi in Gaia.

 ============================================================================================
 |                                    ! HEEEEY, TU !                                        |
 ============================================================================================
  Prima di avventurarti da queste parti, assicurati di leggere la documentazione a:
   https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ============================================================================================
"""


def espandi_persona(persona, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione
    from ufficio_soci.models import Quota, Tesserino
    return [
        (LETTURA,   Trasferimento.objects.filter(persona=persona)),
        (LETTURA,   Estensione.objects.filter(persona=persona)),
        (LETTURA,   Quota.objects.filter(persona=persona)),
        (LETTURA,   Tesserino.objects.filter(persona=persona)),
    ]


def espandi_gestione_soci(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione, Riserva
    from ufficio_soci.models import Quota, Tesserino
    return [
        (MODIFICA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze"))),
        (MODIFICA,  Trasferimento.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze"))),
        (LETTURA,   Trasferimento.objects.filter(destinazione__in=qs_sedi)),
        (MODIFICA,  Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze"))),
        (LETTURA,   Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze"))),
        (LETTURA,   Estensione.objects.filter(destinazione__in=qs_sedi)),
        (MODIFICA,  Quota.objects.filter(sede__in=qs_sedi)),
        (LETTURA,   Riserva.objects.filter(appartenenza__sede__in=qs_sedi)),
    ]


def espandi_emissione_tesserini(qs_sedi, al_giorno=None):
    from ufficio_soci.models import Quota, Tesserino
    return [
        (MODIFICA,  Tesserino.objects.filter(emesso_da__in=qs_sedi)),
    ]


def espandi_elenchi_soci(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza, Sede, Riserva
    from ufficio_soci.models import Quota, Tesserino
    return [
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze"))),
        (LETTURA,  Quota.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze"))),
        (LETTURA,  Quota.objects.filter(Q(Q(sede__in=qs_sedi) | Q(appartenenza__sede__in=qs_sedi)))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, confermata=True, ritirata=False).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.con_esito_pending(sede__in=qs_sedi).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.con_esito_no(sede__in=qs_sedi).via("appartenenze"))),
        (LETTURA,  Riserva.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, confermata=True, ritirata=False).via("persona__appartenenze"))),
        (LETTURA,  Tesserino.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, confermata=True, ritirata=False).via("persona__appartenenze"))),
    ]

def espandi_rubrica_ufficio_soci(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi),
    ]

def espandi_rubrica_ufficio_soci_unita(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_presidenti(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi),
    ]

def espandi_rubrica_delegati_area(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_delegati_obiettivo_1(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_delegati_obiettivo_2(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_delegati_obiettivo_3(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_delegati_obiettivo_4(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_delegati_obiettivo_6(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_delegati_giovani(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_responsabili_area(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_referenti_attivita(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_referenti_gruppi(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_centrali_operative(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_responsabili_formazione(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_direttori_corsi(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_rubrica_responsabili_autoparco(qs_sedi, al_giorno=date.today()):
    return [
        (LETTURA, qs_sedi)
    ]

def espandi_gestione_sede(qs_sedi, al_giorno=None):
    from anagrafica.models import Sede
    return [
        (GESTIONE,  qs_sedi),
    ]


def espandi_gestione_attivita_sede(qs_sedi, al_giorno=None):
    from attivita.models import Attivita
    return [
        (COMPLETO,  Attivita.objects.filter(sede__in=qs_sedi.espandi())),
    ] \
        + espandi_gestione_attivita(Attivita.objects.filter(sede__in=qs_sedi.espandi()))


def espandi_gestione_aree_sede(qs_sedi, al_giorno=None):
    from attivita.models import Area
    from anagrafica.models import Sede
    return [
        (COMPLETO,  Area.objects.filter(sede__in=qs_sedi)),
    ]


def espandi_gestione_attivita_area(qs_aree, al_giorno=None):
    from attivita.models import Attivita
    return [
        (COMPLETO,  Attivita.objects.filter(area__in=qs_aree)),
    ] \
        + espandi_gestione_attivita(Attivita.objects.filter(area__in=qs_aree))


def espandi_gestione_attivita(qs_attivita, al_giorno=None):
    from anagrafica.models import Persona
    return [
        (MODIFICA,  qs_attivita),
        (LETTURA,   Persona.objects.filter(partecipazioni__turno__attivita__in=qs_attivita))
    ]


def espandi_gestione_centrale_operativa_sede(qs_sedi, al_giorno=None):
    from anagrafica.models import Persona, Appartenenza
    return [
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi).via("appartenenze"), reperibilita__isnull=False)),
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi).via("appartenenze"), coturni__isnull=False)),
    ]


def espandi_gestione_poteri_centrale_operativa_sede(qs_sedi, al_giorno=None):
    return [

    ]


def espandi_gestione_referenti_attivita(qs_attivita, al_giorno=None):
    return [
    ]


def espandi_gestione_autoparchi_sede(qs_sedi, al_giorno=None):
    from veicoli.models import Autoparco, Veicolo, Collocazione
    return [
        (MODIFICA,  Autoparco.objects.filter(sede__in=qs_sedi.espandi())),
        (MODIFICA,  Veicolo.objects.filter(Collocazione.query_attuale().via("collocazioni"),
                                           collocazioni__autoparco__sede__in=qs_sedi.espandi())),
        (MODIFICA,  Collocazione.query_attuale(autoparco__sede__in=qs_sedi.espandi())),
    ]


def espandi_gestione_corsi_sede(qs_sedi, al_giorno=None):
    from formazione.models import CorsoBase
    return [
        (COMPLETO,  CorsoBase.objects.filter(sede__in=qs_sedi)),
    ] \
        + espandi_gestione_corso(CorsoBase.objects.filter(sede__in=qs_sedi))


def espandi_gestione_corso(qs_corsi, al_giorno=None):
    from anagrafica.models import Persona
    from formazione.models import PartecipazioneCorsoBase
    return [
        (MODIFICA,  qs_corsi),
        (MODIFICA,  Persona.objects.filter(partecipazioni_corsi__corso__in=qs_corsi).exclude(aspirante__id__isnull=True)),
        (MODIFICA,  PartecipazioneCorsoBase.objects.filter(corso__in=qs_corsi)),
        (LETTURA,   Persona.objects.filter(partecipazioni_corsi__corso__in=qs_corsi)),
    ]


def espandi_gestione_gruppo(qs_gruppi, al_giorno=None):
    from anagrafica.models import Persona
    from gruppi.models import Appartenenza
    return [
        (MODIFICA,  qs_gruppi),
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno).via("appartenenze_gruppi"),
                                           appartenenze_gruppi__gruppo__in=qs_gruppi)),
    ]


def espandi_gestione_gruppi_sede(qs_sedi, al_giorno=None):
    from gruppi.models import Gruppo
    return [

    ] + espandi_gestione_gruppo(Gruppo.objects.filter(sede__in=qs_sedi), al_giorno=al_giorno)


ESPANDI_PERMESSI = {
    GESTIONE_SOCI:                      espandi_gestione_soci,
    ELENCHI_SOCI:                       espandi_elenchi_soci,
    EMISSIONE_TESSERINI:                espandi_emissione_tesserini,
    GESTIONE_SEDE:                      espandi_gestione_sede,
    GESTIONE_AREE_SEDE:                 espandi_gestione_aree_sede,
    GESTIONE_ATTIVITA_SEDE:             espandi_gestione_attivita_sede,
    GESTIONE_ATTIVITA_AREA:             espandi_gestione_attivita_area,
    GESTIONE_REFERENTI_ATTIVITA:        espandi_gestione_referenti_attivita,
    GESTIONE_ATTIVITA:                  espandi_gestione_attivita,
    GESTIONE_CORSI_SEDE:                espandi_gestione_corsi_sede,
    GESTIONE_CORSO:                     espandi_gestione_corso,
    GESTIONE_AUTOPARCHI_SEDE:           espandi_gestione_autoparchi_sede,
    GESTIONE_GRUPPO:                    espandi_gestione_gruppo,
    GESTIONE_GRUPPI_SEDE:               espandi_gestione_gruppi_sede,
    GESTIONE_CENTRALE_OPERATIVA_SEDE:   espandi_gestione_centrale_operativa_sede,
    GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE:    espandi_gestione_poteri_centrale_operativa_sede,
    RUBRICA_UFFICIO_SOCI:               espandi_rubrica_ufficio_soci,
    RUBRICA_UFFICIO_SOCI_UNITA:         espandi_rubrica_ufficio_soci_unita,
    RUBRICA_PRESIDENTI:                 espandi_rubrica_presidenti,
    RUBRICA_DELEGATI_AREA:              espandi_rubrica_delegati_area,
    RUBRICA_DELEGATI_OBIETTIVO_1:       espandi_rubrica_delegati_obiettivo_1,
    RUBRICA_DELEGATI_OBIETTIVO_2:       espandi_rubrica_delegati_obiettivo_2,
    RUBRICA_DELEGATI_OBIETTIVO_3:       espandi_rubrica_delegati_obiettivo_3,
    RUBRICA_DELEGATI_OBIETTIVO_4:       espandi_rubrica_delegati_obiettivo_4,
    RUBRICA_DELEGATI_OBIETTIVO_6:       espandi_rubrica_delegati_obiettivo_6,
    RUBRICA_DELEGATI_GIOVANI:           espandi_rubrica_delegati_giovani,
    RUBRICA_RESPONSABILI_AREA:          espandi_rubrica_responsabili_area,
    RUBRICA_REFERENTI_ATTIVITA:         espandi_rubrica_referenti_attivita,
    RUBRICA_REFERENTI_GRUPPI:           espandi_rubrica_referenti_gruppi,
    RUBRICA_CENTRALI_OPERATIVE:         espandi_rubrica_centrali_operative,
    RUBRICA_RESPONSABILI_FORMAZIONE:    espandi_rubrica_responsabili_formazione,
    RUBRICA_DIRETTORI_CORSI:            espandi_rubrica_direttori_corsi,
    RUBRICA_RESPONSABILI_AUTOPARCO:     espandi_rubrica_responsabili_autoparco,
}
