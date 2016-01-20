from datetime import date

__author__ = 'alfioemanuele'

from anagrafica.permessi.costanti import GESTIONE_SOCI, ELENCHI_SOCI, GESTIONE_ATTIVITA_SEDE, GESTIONE_CORSI_SEDE, \
    GESTIONE_SEDE, GESTIONE_ATTIVITA_AREA, GESTIONE_ATTIVITA, GESTIONE_CORSO, MODIFICA, LETTURA, COMPLETO, \
    GESTIONE_AUTOPARCHI_SEDE, GESTIONE_GRUPPO, GESTIONE_GRUPPI_SEDE, GESTIONE

"""
Questo file gestisce la espansione dei permessi in Gaia.

 ============================================================================================
 |                                    ! HEEEEY, TU !                                        |
 ============================================================================================
  Prima di avventurarti da queste parti, assicurati di leggere la documentazione a:
   https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ============================================================================================
"""


def espandi_persona(persona, al_giorno=date.today()):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione
    return [
        (LETTURA,   Trasferimento.objects.filter(persona=persona)),
        (LETTURA,   Estensione.objects.filter(persona=persona)),
    ]


def espandi_gestione_soci(qs_sedi, al_giorno=date.today()):
    from anagrafica.models import Persona, Appartenenza, Trasferimento, Estensione, Riserva
    from ufficio_soci.models import Quota
    return [
        (MODIFICA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze"))),
        (MODIFICA,   Trasferimento.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze"))),
        ##(LETTURA,   Trasferimento.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze__precedente")))
        (MODIFICA,   Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("persona__appartenenze"))),
        (LETTURA,   Estensione.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze"))),
        (MODIFICA, Quota.objects.filter(sede__in=qs_sedi.espandi())),
        (LETTURA, Riserva.objects.filter(appartenenza__sede__in=qs_sedi.espandi()))
    ]


def espandi_elenchi_soci(qs_sedi, al_giorno=date.today()):
    from anagrafica.models import Persona, Appartenenza, Sede, Riserva
    from ufficio_soci.models import Quota
    return [
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi.espandi()).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("appartenenze"))),
        (LETTURA,  Quota.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ESTESO).via("persona__appartenenze"))),
        (LETTURA,  Quota.objects.filter(sede__in=qs_sedi.espandi())),
        (LETTURA,  Persona.objects.filter(Appartenenza.con_esito_ok(sede__in=qs_sedi.espandi()).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.con_esito_pending(sede__in=qs_sedi.espandi()).via("appartenenze"))),
        (LETTURA,  Persona.objects.filter(Appartenenza.con_esito_no(sede__in=qs_sedi.espandi()).via("appartenenze"))),
        (LETTURA,  Riserva.objects.filter(Appartenenza.con_esito_ok(sede__in=qs_sedi.espandi()).via("persona__appartenenze")))
    ]


def espandi_gestione_sede(qs_sedi, al_giorno=date.today()):
    from anagrafica.models import Sede
    return [
        (GESTIONE,  qs_sedi),
        (GESTIONE,  qs_sedi.espandi()),
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


def espandi_gestione_autoparchi_sede(qs_sedi, al_giorno=date.today()):
    from veicoli.models import Autoparco, Veicolo, Collocazione
    return [
        (MODIFICA,  Autoparco.objects.filter(sede__in=qs_sedi)),
        (MODIFICA,  Veicolo.objects.filter(Collocazione.query_attuale().via("collocazioni"),
                                           collocazioni__autoparco__sede__in=qs_sedi.espandi())),
        (MODIFICA,  Collocazione.query_attuale(autoparco__sede__in=qs_sedi.espandi())),
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


def espandi_gestione_gruppo(qs_gruppi, al_giorno=date.today()):
    from anagrafica.models import Persona
    from gruppi.models import Appartenenza
    return [
        (MODIFICA,  qs_gruppi),
        (LETTURA,   Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno).via("appartenenze_gruppi"),
                                           appartenenze_gruppi__gruppo__in=qs_gruppi)),
    ]


def espandi_gestione_gruppi_sede(qs_sedi, al_giorno=date.today()):
    from gruppi.models import Gruppo
    return [

    ] + espandi_gestione_gruppo(Gruppo.objects.filter(sede__in=qs_sedi), al_giorno=al_giorno)


ESPANDI_PERMESSI = {
    GESTIONE_SOCI:          espandi_gestione_soci,
    ELENCHI_SOCI:           espandi_elenchi_soci,
    GESTIONE_SEDE:          espandi_gestione_sede,
    GESTIONE_ATTIVITA_SEDE: espandi_gestione_attivita_sede,
    GESTIONE_ATTIVITA_AREA: espandi_gestione_attivita_area,
    GESTIONE_ATTIVITA:      espandi_gestione_attivita,
    GESTIONE_CORSI_SEDE:    espandi_gestione_corsi_sede,
    GESTIONE_CORSO:         espandi_gestione_corso,
    GESTIONE_AUTOPARCHI_SEDE:espandi_gestione_autoparchi_sede,
    GESTIONE_GRUPPO:        espandi_gestione_gruppo,
    GESTIONE_GRUPPI_SEDE:   espandi_gestione_gruppi_sede,
}