import random
import string
from datetime import timedelta
from codicefiscale import build
import names

from anagrafica.costanti import LOCALE, ESTENSIONE
from anagrafica.models import Persona, Sede, Appartenenza, Delega
from anagrafica.permessi.applicazioni import PRESIDENTE
from attivita.models import Area, Attivita, Turno, Partecipazione
from autenticazione.models import Utenza
from base.geo import Locazione
from base.utils import poco_fa
from jorvik.settings import SELENIUM_DRIVER, SELENIUM_URL, SELENIUM_BROWSER


def codice_fiscale(length=16):
   return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


def codice_fiscale_persona(persona):
    from base.comuni import COMUNI
    try:
        codice_comune = COMUNI[persona.comune_nascita.lower()]
    except KeyError:
        codice_comune = 'D000'
    return build(persona.cognome, persona.nome, persona.data_nascita, persona.genere, codice_comune)


def crea_persona():
    p = Persona.objects.create(
        nome=names.get_first_name(),
        cognome=names.get_last_name(),
        codice_fiscale=codice_fiscale(),
        data_nascita="{}-{}-{}".format(random.randint(1960, 1990), random.randint(1, 12), random.randint(1, 28))
    )
    p.refresh_from_db()
    return p


def crea_utenza(persona, email="mario@rossi.it", password="prova"):
    u = Utenza(
        persona=persona,
        email=email,
    )
    u.save()
    u.set_password(password)
    u.save()
    u.password_testing = password  # Ai fini del testing.
    return u


def crea_sede(presidente=None, estensione=LOCALE, genitore=None,
              locazione=None):
    ESTENSIONE_DICT = dict(ESTENSIONE)
    locazione = locazione or crea_locazione()
    s = Sede(
        nome="Com. " + ESTENSIONE_DICT[estensione] + " " + names.get_last_name(),
        tipo=Sede.COMITATO,
        estensione=estensione,
        genitore=genitore,
        telefono='+3902020202',
        email='comitato@prova.it',
        codice_fiscale='01234567891',
        partita_iva='01234567891',
        locazione=locazione
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


def crea_locazione(dati=None, geo=False):
    if not dati and geo:
        indirizzo = 'Via Toscana, 12 - 00187 Roma'
        geo = Locazione.cerca(indirizzo)
        locazione = Locazione.objects.create(**geo[0][2])
    else:
        if not dati:
            dati = {
                'civico': '99',
                'via': 'via via',
                'comune': 'Roma',
                'provincia': 'RM',
                'regione': 'Lazio',
                'stato': 'IT',
                'cap': '06066',
            }
        locazione = Locazione.objects.create(**dati)
    return locazione


def crea_appartenenza(persona, sede, tipo=Appartenenza.VOLONTARIO):
    return Appartenenza.objects.create(
        persona=persona,
        sede=sede,
        membro=tipo,
        inizio="1980-12-10",
    )


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
                  centrale_operativa=None):
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


def crea_area_attivita(sede, centrale_operativa=None):
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


def crea_sessione(wait_time=5):
    from splinter import Browser
    browser = Browser(driver_name=SELENIUM_DRIVER, url=SELENIUM_URL,
                      browser=SELENIUM_BROWSER,
                      wait_time=wait_time)
    return browser


def email_fittizzia():
    return "email_%d@test.gaia.cri.it" % random.randint(1, 9999999)


def sessione_anonimo(server_url):
    sessione = crea_sessione()
    sessione.visit(server_url)

    # Assicurati che l'apertura sia riuscita.
    assert sessione.is_text_present("Il Progetto Gaia")

    return sessione


def sessione_utente(server_url, persona=None, utente=None, password=None, wait_time=7):
    if not (persona or utente):
        raise ValueError("sessione_utente deve ricevere almeno una persona "
                         "o un utente.")

    if persona:
        try:
            utenza = persona.utenza
        except:
            utenza = crea_utenza(persona=persona, email=email_fittizzia(),
                                 password=names.get_full_name())

    elif utente:
        utenza = utente

    try:
        password_da_usare = password or utenza.password_testing

    except AttributeError:
        raise AttributeError("L'utenza è già esistente, non ne conosco la password.")

    sessione = crea_sessione(wait_time)
    sessione.visit("%s/login/" % server_url)
    sessione.fill("auth-username", utenza.email)
    sessione.fill("auth-password", password_da_usare)
    sessione.find_by_xpath('//button[@type="submit"]').first.click()

    # Assicurati che il login sia riuscito.
    assert sessione.is_text_present(utenza.persona.nome)

    return sessione

