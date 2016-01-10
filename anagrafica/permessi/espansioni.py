from datetime import date

__author__ = 'alfioemanuele'

from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI, GESTIONE_ATTIVITA_SEDE, GESTIONE_CORSI_SEDE, \
    GESTIONE_SEDE, GESTIONE_ATTIVITA_AREA, GESTIONE_ATTIVITA, GESTIONE_CORSO, MODIFICA, LETTURA, COMPLETO

"""
Questo file gestisce la espansione dei permessi in Gaia.

 ============================================================================================
 |                                    ! HEEEEY, TU !                                        |
 ============================================================================================
  Prima di avventurarti da queste parti, assicurati di leggere la documentazione a:
   https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ============================================================================================
"""


def espandi_gestione_soci(qs_sedi, al_giorno=date.today()):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione
    return [
        (MODIFICA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze")))
        (MODIFICA,   Trasferimento.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze")))
        ##(LETTURA,   Trasferimento.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze__precedente")))
        (MODIFICA,   Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze")))
        (LETTURA,   Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze")))
    ]



def espandi_elenchi_soci(qs_sedi, al_giorno=date.today()):
    from anagrafica.models import Persona, Appartenenza, Sede
    return [
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi.espandi()).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze"))),
    ]

def espandi_gestione_sede(qs_sedi, al_giorno=date.today()):
    from anagrafica.models import Sede
    return [
        (MODIFICA,  qs_sedi),
        (MODIFICA,  qs_sedi.espandi()),
    ]

def espandi_gestione_attivita_sede(qs_sedi, al_giorno=date.today()):
    from attivita.models import Attivita
    return [
        (COMPLETO,  Attivita.objects.filter(sede__in=qs_sedi.espandi())),
    ] \
        + espandi_gestione_attivita(Attivita.objects.filter(sede__in=qs_sedi.espandi()))

def espandi_gestione_attivita_area(qs_aree, al_giorno=date.today()):
    from attivita.models import Attivita
    return [
        (COMPLETO,  Attivita.objects.filter(area__in=qs_aree)),
    ] \
        + espandi_gestione_attivita(Attivita.objects.filter(area__in=qs_aree))

def espandi_gestione_attivita(qs_attivita, al_giorno=date.today()):
    from anagrafica.models import Persona
    return [
        (MODIFICA,  qs_attivita),
        (LETTURA,   Persona.objects.filter(partecipazioni__turno__attivita__in=qs_attivita))
    ]

def espandi_gestione_corsi_sede(qs_sedi, al_giorno=date.today()):
    from formazione.models import CorsoBase
    return [
        (COMPLETO,  CorsoBase.objects.filter(sede__in=qs_sedi)),
    ] \
        + espandi_gestione_corso(CorsoBase.objects.filter(sede__in=qs_sedi))

def espandi_gestione_corso(qs_corsi, al_giorno=date.today()):
    from anagrafica.models import Persona
    return [
        (MODIFICA,  qs_corsi),
        (MODIFICA,  Persona.objects.filter(partecipazioni_corsi__corso__in=qs_corsi).exclude(aspirante__id__isnull=True)),
        (LETTURA,   Persona.objects.filter(partecipazioni_corsi__corso__in=qs_corsi)),
    ]


ESPANDI_PERMESSI = {
    GESTIONE_SOCI:          espandi_gestione_soci,
    ELENCHI_SOCI:           espandi_elenchi_soci,
    GESTIONE_SEDE:          espandi_gestione_sede,
    GESTIONE_ATTIVITA_SEDE: espandi_gestione_attivita_sede,
    GESTIONE_ATTIVITA_AREA: espandi_gestione_attivita_area,
    GESTIONE_ATTIVITA:      espandi_gestione_attivita,
    GESTIONE_CORSI_SEDE:    espandi_gestione_corsi_sede,
    GESTIONE_CORSO:         espandi_gestione_corso,
}