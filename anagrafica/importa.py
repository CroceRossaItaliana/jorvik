import datetime
import re

import codicefiscale
import ftfy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.encoding import smart_str

from anagrafica.models import Persona, Sede, Appartenenza
from autenticazione.models import Utenza
from base.stringhe import normalizza_nome
from base.utils import poco_fa
from formazione.models import Aspirante

VALIDAZIONE_OK = "OK"
VALIDAZIONE_AVVISO = "AVVISO"
VALIDAZIONE_ERRORE = "ERRORE"


def stringa(s):
    if s is None:
        return ''
    # try:
    #    #return smart_str(s.encode('utf-8'))
    #except:
    return ftfy.fix_text(smart_str(s), fix_entities=False)


def import_valida_volontario_riga(riga):

    for i in range(0, len(riga)):
        riga[i] = riga[i]

    log = []

    nome = normalizza_nome(stringa(riga[0]))
    if not nome:
        log += [(VALIDAZIONE_ERRORE, "Nome vuoto")]

    cognome = normalizza_nome(stringa(riga[1]))
    if not cognome:
        log += [(VALIDAZIONE_ERRORE, "Cognome vuoto")]

    data_nascita = None

    try:
        data_nascita = datetime.datetime.strptime(riga[2], "%d/%m/%Y").date()
    except ValueError:
        data_nascita = None
        #log += [(VALIDAZIONE_ERRORE, "Data di nascita non valida (gg/mm/YYYY)")]

    if data_nascita and data_nascita < datetime.date(1800, 1, 1):
        log += [(VALIDAZIONE_ERRORE, "Data di nascita errata (prima del 1800)")]

    luogo_nascita = normalizza_nome(stringa(riga[3]))
    luogo_nascita = re.search("(.*) ?\((.*)\)", luogo_nascita)
    #if not luogo_nascita:
    #    log += [(VALIDAZIONE_ERRORE, "Luogo di nascita non valido (Comune (PV))")]

    comune_nascita = luogo_nascita.group(1) if luogo_nascita else None
    provincia_nascita = luogo_nascita.group(2) if luogo_nascita else None

    if provincia_nascita and len(provincia_nascita) > 2:
        provincia_nascita = provincia_nascita[:2]
        #log += [(VALIDAZIONE_ERRORE, "Provincia di nascita non valida (>2 caratteri)")]

    codice_fiscale = riga[4].upper()
    #if not codicefiscale.isvalid(codice_fiscale):
    #    log += [(VALIDAZIONE_ERRORE, "Codice fiscale non valido")]

    sede = stringa(riga[15])
    try:
        sede = Sede.objects.get(nome__iexact=sede)
    except Sede.DoesNotExist:
        try:
            sede = Sede.objects.get(nome__iexact=stringa(riga[16]))
        except:
            log += [(VALIDAZIONE_ERRORE, "Sede non trovata: %s" % (sede,))]
            sede = None


    email = riga[10]
    email_2 = riga[11]
    email = email or email_2

    if email:
        try:
            validate_email(email)
        except ValidationError:
            log += [(VALIDAZIONE_ERRORE, "E-mail non valida")]


    precedente = Persona.objects.filter(codice_fiscale=codice_fiscale).first()
    if sede:
        if precedente:

            presso_mia_sede = precedente.appartenenze_attuali().filter(membro=Appartenenza.VOLONTARIO, sede__in=sede.comitato.espandi(includi_me=True)).first()
            presso_qualche_sede = precedente.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).exists()
            aspirante = Aspirante.objects.filter(persona=precedente).exists()

            if presso_mia_sede:
                log += [(VALIDAZIONE_ERRORE, "Già appartenente come %s presso la sede richiesta di %s" % (presso_mia_sede.get_membro_display(), presso_mia_sede.sede.nome_completo))]

            elif presso_qualche_sede:
                log += [(VALIDAZIONE_ERRORE, "Già appartenente presso Sede fuori da %s" % (sede.comitato.nome,))]

            elif aspirante:
                log += [(VALIDAZIONE_AVVISO, "Persona pre-esistente in Gaia, iscritta come aspirante. Verrà aggiornata la "
                                             "sua appartenenza e disattivata la possibilita di partecipare a nuovi corsi base. ")]

            else:
                log += [(VALIDAZIONE_AVVISO, "Esiste in Gaia ma senza alcuna appartenenza come volontario")]

        else:

            # log += [(VALIDAZIONE_AVVISO, "Non pre-esistente in Gaia")]

            if email and Utenza.objects.filter(email__iexact=email).exists():
                log += [(VALIDAZIONE_AVVISO, "Impossibile attivare credenziali automaticamente, email gia esistente (%s), "
                                             "sarà necessario attivare delle credenziali manualmente dal pannello credenziali"
                                             " della sua scheda." % (email,))]

            elif not email:
                log += [(VALIDAZIONE_AVVISO, "Impossibile attivare credenziali automaticamente, email non specificata, "
                             "sarà necessario attivare delle credenziali manualmente dal pannello credenziali"
                             " della sua scheda.")]




    indirizzo_residenza = "%s, %s" % (riga[5], riga[6])
    if indirizzo_residenza == ", ":
        indirizzo_residenza = ""

    comune_residenza = stringa(riga[7])
    #if not comune_residenza:
    #    log += [(VALIDAZIONE_ERRORE, "Comune di residenza obbligatorio")]

    provincia_residenza = stringa(riga[8])
    #if not provincia_residenza:
    #    log += [(VALIDAZIONE_ERRORE, "Provincia di residenza obbligatorio")]

    cap = riga[9]
    #if not cap:
    #    log += [(VALIDAZIONE_ERRORE, "CAP di residenza obbligatorio")]

    telefono = riga[12]
    telefono_servizio = riga[13]

    data_ingresso = None
    try:
        data_ingresso = datetime.datetime.strptime(riga[14], "%d/%m/%Y").date()
    except ValueError:
        log += [(VALIDAZIONE_ERRORE, "Data di ingresso non valida (gg/mm/YYYY)")]

    if data_ingresso and data_ingresso < datetime.date(1800, 1, 1):
        log += [(VALIDAZIONE_ERRORE, "Data di ingresso errata (prima del 1800)")]

    if not _ha_errore(log):
        log += [
            (VALIDAZIONE_OK,
             {
                 "nome": nome,
                 "cognome": cognome,
                 "data_nascita": data_nascita,
                 "comune_nascita": comune_nascita,
                 "provincia_nascita": provincia_nascita,
                 "codice_fiscale": codice_fiscale,
                 "indirizzo_residenza": indirizzo_residenza,
                 "comune_residenza": comune_residenza,
                 "provincia_residenza": provincia_residenza,
                 "stato_nascita": "IT",
                 "stato_residenza": "IT",
                 "cap_residenza": cap,
                 "email_contatto": email,
                 "email": email,
                 "telefono": telefono,
                 "telefono_servizio": telefono_servizio,
                 "data_ingresso": data_ingresso,
                 "sede": sede,
             }
             )
        ]

    return log


def _ha_errore(risultato):
    for riga in risultato:
        if riga[0] == VALIDAZIONE_ERRORE:
            return True
    return False

def _ottieni_dati(risultato):
    for riga in risultato:
        if riga[0] == VALIDAZIONE_OK:
            return riga[1]
    raise ValueError("Non ci sono dati qui")


def import_valida_volontari(righe):
    risultato = []
    for riga in righe:
        validazione = import_valida_volontario_riga(riga)
        risultato += [validazione]
    return risultato


def import_import_volontari(risultato):
    i = 0
    for p in risultato:
        if _ha_errore(p):
            continue

        dati = _ottieni_dati(p)

        dati_persona = {x: y for x, y in dati.items() if x in [
            "nome", "cognome", "codice_fiscale", "data_nascita", "comune_nascita",
            "provincia_nascita", "stato_nascita", "stato_residenza",
            "cap_residenza", "indirizzo_residenza", "comune_residenza",
            "email_contatto"
        ]}

        try:
            persona = Persona.objects.get(codice_fiscale__iexact=dati_persona['codice_fiscale'])

        except Persona.DoesNotExist:
            persona = Persona(**dati_persona)
            persona.save()

        if dati['telefono']:
            persona.aggiungi_numero_telefono(dati['telefono'], servizio=False)

        if dati['telefono_servizio']:
            persona.aggiungi_numero_telefono(dati['telefono_servizio'], servizio=True)

        for app in persona.appartenenze_attuali():
            app.fine = poco_fa()
            app.save()

        # Cancella aspirante associato
        Aspirante.objects.filter(persona=persona).delete()

        app = Appartenenza(
            persona=persona,
            sede=dati['sede'],
            inizio=dati['data_ingresso'],
            membro=Appartenenza.VOLONTARIO,
        )
        app.save()

        if dati['email'] and not Utenza.objects.filter(persona=persona).exists():
            # Non ha utenza
            if not Utenza.objects.filter(email__iexact=dati['email']):
                # Non esiste, prova a creare
                u = Utenza(persona=persona, email=dati['email'])
                u.save()
                u.genera_credenziali()

        i += 1

    return i
