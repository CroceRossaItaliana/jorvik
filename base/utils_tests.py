import random
import string
from datetime import timedelta

import names

from anagrafica.costanti import LOCALE, ESTENSIONE
from anagrafica.models import Persona, Sede, Appartenenza, Delega
from anagrafica.permessi.applicazioni import PRESIDENTE
from attivita.models import Area, Attivita, Turno, Partecipazione
from base.utils import poco_fa


def codice_fiscale(length=16):
   return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def crea_persona():
    p = Persona(
        nome=names.get_first_name(),
        cognome=names.get_last_name(),
        codice_fiscale=codice_fiscale(),
        data_nascita="1994-2-5"
    )
    p.save()
    return p

def crea_sede(presidente=None, estensione=LOCALE, genitore=None):
    ESTENSIONE_DICT = dict(ESTENSIONE)
    s = Sede(
        nome="Com. " + ESTENSIONE_DICT[estensione] + " " + names.get_last_name(),
        tipo=Sede.COMITATO,
        estensione=estensione,
        genitore=genitore,
    )
    s.save()
    if presidente is not None:
        d = Delega(
            inizio="1980-12-10",
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=s
        )
        d.save()
    return s


def crea_appartenenza(persona, sede):
    app = Appartenenza(
        persona=persona,
        sede=sede,
        membro=Appartenenza.VOLONTARIO,
        inizio="1980-12-10",
    )
    app.save()
    return app


def crea_persona_sede_appartenenza(presidente=None):
    p = crea_persona()
    s = crea_sede(presidente)
    a = crea_appartenenza(p, s)
    return p, s, a


def crea_area(sede):
    area = Area(
        nome="6",
        obiettivo=6,
        sede=sede,
    )
    area.save()
    return area


def crea_attivita(sede, area, nome="Attivita di test",
                  stato=Attivita.APERTA, descrizione="Descrizione",
                  centrale_operativa=False):
    attivita = Attivita(
        sede=sede,
        area=area,
        estensione=sede,
        nome=nome,
        stato=stato,
        descrizione=descrizione,
        centrale_operativa=centrale_operativa,
    )
    attivita.save()
    return attivita


def crea_area_attivita(sede, centrale_operativa=False):
    area = crea_area(sede)
    attivita = crea_attivita(sede, area, centrale_operativa=centrale_operativa)
    return area, attivita


def crea_turno(attivita, inizio=None, fine=None, prenotazione=None,
               minimo=1, massimo=10):
    inizio = inizio or poco_fa()
    fine = fine or poco_fa() + timedelta(hours=2)
    prenotazione = prenotazione or inizio - timedelta(hours=1)
    turno = Turno(
        attivita=attivita,
        inizio=inizio,
        fine=fine,
        prenotazione=prenotazione,
        minimo=minimo,
        massimo=massimo,
        nome="Turno di test",
    )
    turno.save()
    return turno


def crea_partecipazione(persona, turno):
    p = Partecipazione(
        turno=turno,
        persona=persona,
        stato=Partecipazione.RICHIESTA,
    )
    p.save()
    return p
