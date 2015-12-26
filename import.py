# -*- coding: utf-8 -*-

import os, sys

import phonenumbers


os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
from anagrafica.permessi.applicazioni import PRESIDENTE, DELEGATO_AREA, REFERENTE, DELEGATO_OBIETTIVO_1, \
    DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, \
    DELEGATO_CO, UFFICIO_SOCI, RESPONSABILE_PATENTI, RESPONSABILE_FORMAZIONE, UFFICIO_SOCI_TEMPORANEO, \
    RESPONSABILE_AUTOPARCO, RESPONSABILE_DONAZIONI, DIRETTORE_CORSO
from attivita.models import Area, Attivita, Partecipazione, Turno
from base.models import Autorizzazione
from curriculum.models import TitoloPersonale, Titolo
from social.models import Commento

import pickle
import sangue.models as sangue
from django.contrib.gis.geos import Point
from autenticazione.models import Utenza
import formazione.models as formazione

from safedelete import HARD_DELETE
from jorvik.settings import MYSQL_CONF

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.template.backends import django
from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from anagrafica.models import Sede, Persona, Appartenenza, Delega, Trasferimento
from base.geo import Locazione
from ufficio_soci.models import Quota, Tesseramento
import argparse
import ftfy

from datetime import datetime, date
from django.utils import timezone

__author__ = 'alfioemanuele'

import MySQLdb

def stringa(s):
    if s is None:
        return ''
    # try:
    #    #return str(s.encode('utf-8'))
    #except:
    return ftfy.fix_text(str(s), fix_entities=False)

parser = argparse.ArgumentParser(description='Importa i dati da un database MySQL di PHP-Gaia.')
parser.add_argument('--no-geo', dest='geo', action='store_const',
                   const=False, default=True,
                   help='disattiva le funzionalità geografiche (solo test)')
parser.add_argument('-v', dest='verbose', action='store_const',
                   const=True, default=False,
                   help='mostra dettagli sul progresso (estremamente prolisso)')
parser.add_argument('--salta-comitati', dest='comitati', action='store_const',
                   const=False, default=True,
                   help='salta importazione comitati (usa cache precedente)')
parser.add_argument('--salta-anagrafiche', dest='anagrafiche', action='store_const',
                   const=False, default=True,
                   help='salta importazione anagrafiche (usa cache precedente)')
parser.add_argument('--salta-appartenenze', dest='appartenenze', action='store_const',
                   const=False, default=True,
                   help='salta importazione appartenenze (usa cache precedente)')
parser.add_argument('--salta-deleghe', dest='deleghe', action='store_const',
                   const=False, default=True,
                   help='salta importazione deleghe (usa cache precedente)')
parser.add_argument('--salta-aree', dest='aree', action='store_const',
                   const=False, default=True,
                   help='salta importazione aree (usa cache precedente)')
parser.add_argument('--salta-attivita', dest='attivita', action='store_const',
                   const=False, default=True,
                   help='salta importazione attivita (usa cache precedente)')
parser.add_argument('--salta-turni', dest='turni', action='store_const',
                   const=False, default=True,
                   help='salta importazione turni (usa cache precedente)')
parser.add_argument('--salta-partecipazioni', dest='partecipazioni', action='store_const',
                   const=False, default=True,
                   help='salta importazione partecipazioni (usa cache precedente)')
parser.add_argument('--salta-quote', dest='quote', action='store_const',
                   const=False, default=True,
                   help='salta importazione quote (usa cache precedente)')
parser.add_argument('--salta-titoli', dest='titoli', action='store_const',
                   const=False, default=True,
                   help='salta importazione titoli e titoli personali (usa cache precedente)')
parser.add_argument('--salta-sangue', dest='sangue', action='store_const',
                   const=False, default=True,
                   help='salta importazione donazioni di sangue (usa cache precedente)')
parser.add_argument('--salta-commenti', dest='commenti', action='store_const',
                   const=False, default=True,
                   help='salta importazione commenti alle attivita (usa cache precedente)')
parser.add_argument('--salta-corsibase', dest='corsibase', action='store_const',
                   const=False, default=True,
                   help='salta importazione corsi base e relativi (usa cache precedente)')
parser.add_argument('--salta-aspiranti', dest='aspiranti', action='store_const',
                   const=False, default=True,
                   help='salta importazione aspiranti e localizzazione (usa cache precedente)')
parser.add_argument('--salta-trasferimenti', dest='trasferimenti', action='store_const',
                   const=False, default=True,
                   help='salta importazione trasferimenti (usa cache precedente)')
parser.add_argument('--ignora-errori-db', dest='ignora', action='store_const',
                   const=True, default=False,
                   help='ignora errori di integrità (solo test)')

args = parser.parse_args()


# .conect(host, username, password, database)
db = MySQLdb.connect(
    MYSQL_CONF.get('client', 'host'),
    MYSQL_CONF.get('client', 'user'),
    MYSQL_CONF.get('client', 'password'),
    MYSQL_CONF.get('client', 'database'),
    use_unicode=True,
    charset="utf8"
)

## IMPORTA COMITATI
COMITATO_INFERIORE = {
    'nazionali': 'regionali',
    'regionali': 'provinciali',
    'provinciali': 'locali',
    'locali': 'comitati',
    'comitati': None
}
COMITATO_ESTENSIONE = {
    'nazionali': NAZIONALE,
    'regionali': REGIONALE,
    'provinciali': PROVINCIALE,
    'locali': LOCALE,
    'comitati': TERRITORIALE
}
COMITATO_ESTENSIONE_COSTANTE = {
    10: TERRITORIALE,
    20: LOCALE,
    30: PROVINCIALE,
    40: REGIONALE,
    80: NAZIONALE,
}
COMITATO_GENITORE = {
    'nazionali': None,
    'regionali': 'nazionale',
    'provinciali': 'regionale',
    'locali': 'provinciale',
    'comitati': 'locale'
}
COMITATO_DATI = {
    'nazionali': 'datiNazionali',
    'regionali': 'datiRegionali',
    'provinciali': 'datiProvinciali',
    'locali': 'datiLocali',
    'comitati': 'datiComitati'
}
COMITATO_OID = {
    'nazionali': 'Nazionale',
    'regionali': 'Regionale',
    'provinciali': 'Provinciale',
    'locali': 'Locale',
    'comitati': 'Comitato'
}

# Questo dizionario mantiene le associazioni ID/OID
#  es. ASSOC_ID['Nazionale'][1] = (Sede, 1)
ASSOC_ID_COMITATI = {
    'Nazionale': {},
    'Regionale': {},
    'Provinciale': {},
    'Locale': {},
    'Comitato': {},
}

# Questo dizionario mantiene le associazioni ID persone
#  es. ASSOC_ID_PERSONE[123] = 4422
ASSOC_ID_PERSONE = {}

# Questo dizionario mantiene le associazioni ID appartenenze
#  es. ASSOC_ID_APPARTENENZE[123] = 4444
ASSOC_ID_APPARTENENZE = {}

# Questo dizionario mantiene le associazioni ID appartenenze
#  es. ASSOC_ID_DELEGHE[123] = 4444
ASSOC_ID_DELEGHE = {}

# Questo dizionario mantiene le associazioni ID delle aree
#  es. ASSOC_ID_AREE[123] = 444
ASSOC_ID_AREE = {}

# Questo dizionario mantiene le associazioni ID delle attivita
#  es. ASSOC_ID_ATTIVITA[123] = 465
ASSOC_ID_ATTIVITA = {}

# Questo dizionario mantiene le associazioni ID dei turni
#  es. ASSOC_ID_TURNI[123] = 465
ASSOC_ID_TURNI = {}

# Questo dizionario mantiene le associazioni ID delle partecipazioni
#  es. ASSOC_ID_PARTECIPAZIONI[123] = 465
ASSOC_ID_PARTECIPAZIONI = {}

# Questo dizionario mantiene le associazioni ID dei tesseramenti
ASSOC_ID_TESSERAMENTI = {}

# Questo dizionario mantiene le associazioni ID delle quote
ASSOC_ID_QUOTE = {}

# Questo dizionario mantiene le associazioni ID dei titoli
ASSOC_ID_TITOLI = {}

# Questo dizionario mantiene le associazioni ID delle quote
ASSOC_ID_TITOLIPERSONALI = {}

# Dizionari per il modulo donazioni sangue
ASSOC_ID_SANGUE_DONATORI = {}
ASSOC_ID_SANGUE_DONAZIONI = {}
ASSOC_ID_SANGUE_MERITI = {}
ASSOC_ID_SANGUE_SEDI = {}

# Dizionario per il modulo social
ASSOC_ID_COMMENTI = {}

# Dizionario per il modulo corsi base
ASSOC_ID_CORSIBASE = {}
ASSOC_ID_CORSIBASE_LEZIONI = {}
ASSOC_ID_CORSIBASE_ASSENZE = {}
ASSOC_ID_CORSIBASE_PARTECIPAZIONI = {}

ASSOC_ID_ASPIRANTI = {}

ASSOC_ID_TRASFERIMENTI = {}


def parse_numero(numero, paese="IT"):
    try:
        n = phonenumbers.parse(numero, paese)
    except phonenumbers.phonenumberutil.NumberParseException:
        return numero
    f = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
    return f

def progresso(contatore, totale):
    percentuale = contatore / float(totale) * 100.0
    return "%.2f%% (%d su %d) " % (percentuale, contatore, totale)

def ottieni_comitato(tipo='nazionali', id=1):
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, nome, X(geo), Y(geo)""" + (", principale" if tipo == 'comitati' else " ") + """
        FROM
            """ + tipo + """
        WHERE id = %s
        """, (id,)
    )
    comitato = cursore.fetchone()
    cursore.execute("""
        SELECT
            id, nome, valore
        FROM
            """ + COMITATO_DATI[tipo] + """
        WHERE id = %s
        """, (id,)
    )
    dati = cursore.fetchall()
    dict = {}
    for (id, nome, valore) in dati:
        dict.update({nome: valore})
    return {
        'id': comitato[0],
        'nome': comitato[1],
        'x': comitato[2],
        'y': comitato[3],
        'dati': dict
    }

def mysql_copia_tabella_in_memoria(vecchia, nuova, campi_text=[], indici=['id']):
    query = "DROP TABLE IF EXISTS " + nuova + ";\n"
    for campo in campi_text:
        query += "ALTER TABLE " + vecchia + " MODIFY " + campo + " VARCHAR(256);\n"
    query += "CREATE TABLE " + nuova + " SELECT * FROM " + vecchia + " WHERE 1=2;\n"
    query += "ALTER TABLE " + nuova + " ENGINE=MEMORY;\n"
    for indice in indici:
        query += "ALTER TABLE " + nuova + " ADD INDEX (" + indice + ") USING HASH ;\n"
    query += "INSERT INTO " + nuova + " SELECT * FROM " + vecchia + ";\n"
    cursore = db.cursor()
    cursore.execute(query)
    cursore.close()

def mysql_cancella_tabella(tabella):
    query = "DROP TABLE " + tabella + ";\n"
    cursore = db.cursor()
    cursore.execute(query)
    cursore.close()

def data_da_timestamp(timestamp, default=timezone.now()):
    if not timestamp:
        return default
    timestamp = int(timestamp)
    if not timestamp:  # timestamp 0, 1970-1-1
        return default
    try:
        return timezone.now().fromtimestamp(timestamp)
    except ValueError:
        return default

def ottieni_figli(tipo='nazionali', id=1):
    if COMITATO_INFERIORE[tipo] is None:
        return []
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id
        FROM
            """ + COMITATO_INFERIORE[tipo] + """
        WHERE """ + COMITATO_GENITORE[COMITATO_INFERIORE[tipo]] + """ = %s
        """, (id,)
    )
    figli = cursore.fetchall()
    cursore.close()
    figli = [(COMITATO_INFERIORE[tipo], x[0]) for x in figli]
    return figli

def carica_anagrafiche():
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, nome, cognome, stato, email, password,
            codiceFiscale, timestamp, admin, consenso, sesso
        FROM
            anagrafica
        WHERE
            codiceFiscale IS NOT NULL
        AND nome IS NOT NULL
        AND cognome IS NOT NULL
        """
    )
    persone = cursore.fetchall()

    if args.verbose:
        print("  - Creazione dizionario dettagli schede")

    cursore.execute("""
        SELECT
            id, nome, valore
        FROM
            dettagliPersona
        """
    )
    dettagli = cursore.fetchall()
    DETTAGLI_DICT = {}
    for riga in dettagli:
        attuale = DETTAGLI_DICT.get(int(riga[0]), {})
        attuale.update({riga[1]: riga[2]})
        DETTAGLI_DICT.update({int(riga[0]): attuale})

    print(DETTAGLI_DICT[218])

    totale = cursore.rowcount
    contatore = 0
    for persona in persone:

        contatore += 1

        if args.verbose:
            print("    - " + progresso(contatore, totale) + ": id=" + stringa(persona[0]) + ", codice_fiscale=" + stringa(persona[6]))
            print("      - Scaricamento dati aggiuntivi")

        id = persona[0]

        dict = DETTAGLI_DICT.get(int(persona[0]), {})
        dati = {
            'id': persona[0],
            'nome': stringa(persona[1]),
            'cognome': stringa(persona[2]),
            'stato': persona[3],
            'email': persona[4],
            'password': persona[5],
            'codiceFiscale': persona[6].upper(),
            'timestamp': persona[7],
            'admin': persona[8],
            'consenso': persona[9],
            'sesso': persona[10],
            'dettagliPersona': dict
        }

        #print(dati)
        if args.verbose:
            print("      - Creazione della scheda anagrafica")

        provincia_residenza = stringa(dict.get('provinciaResidenza')[0:2]) if dict.get('provinciaResidenza') else ''
        provincia_nascita = stringa(dict.get('provinciaNascita')[0:2]) if dict.get('provinciaNascita') else provincia_residenza
        data_nascita = data_da_timestamp(dict.get('dataNascita'), default=None)
        p = Persona(
            nome=dati['nome'],
            cognome=dati['cognome'],
            codice_fiscale=dati['codiceFiscale'],
            data_nascita=data_nascita,
            genere=Persona.MASCHIO if dati['sesso'] == 1 else Persona.FEMMINA,
            stato=Persona.PERSONA,
            comune_nascita=stringa(dict.get('comuneNascita')) if dict.get('comuneNascita') else '',
            provincia_nascita=provincia_nascita,
            stato_nascita='IT',
            indirizzo_residenza=stringa(dict.get('indirizzo')) + ", " + stringa(dict.get('civico')),
            comune_residenza=stringa(dict.get('comuneResidenza')) if dict.get('comuneResidenza') else '',
            provincia_residenza=provincia_residenza,
            stato_residenza='IT',
            cap_residenza=dict.get('CAPResidenza') if dict.get('CAPResidenza') else '',
            email_contatto=dict.get('emailServizio', ''),
            creazione=data_da_timestamp(dict.get('timestamp')),
            vecchio_id=int(id),
        )
        try:
            p.save()
        except IntegrityError:
            if args.verbose:
                print("    - CF DUPLICATO: Unione...")
                p = Persona.objects.filter(codice_fiscale=dati['codiceFiscale'])
                if not p:
                    raise
                p = p[0]


        # Se anagrafica attiva (ha accesso), crea Utenza
        if dati['email']:

            if args.verbose:
                print("      - Utenza attiva " + stringa(dati['email']))

            u = Utenza(
                persona=p,
                ultimo_accesso=datetime.fromtimestamp(int(dict.get('ultimoAccesso', None))) if dict.get('ultimoAccesso', None) else None,
                ultimo_consenso=datetime.fromtimestamp(int(dati['consenso'])) if dati['consenso'] else None,
                email=dati['email'],
                is_staff=True if dati['admin'] else False,
                is_superuser=True if dati['admin'] else False,
            )

            if (dati['password']):
                u.password = "gaia$1$$" + dati['password']

            else:
                u.set_unusable_password()

            try:
                u.save()

            except:
                if args.ignora:
                    print("    ERRORE DATABASE IGNORATO")
                    continue
                else:
                    raise

        if dict.get('cellulare', False):
            if args.verbose:
                print("      - Numero cellulare personale " + stringa(dict.get('cellulare')))
            p.aggiungi_numero_telefono(dict.get('cellulare'), False)

        if dict.get('cellulareServizio', False):
            if args.verbose:
                print("      - Numero cellulare servizio " + stringa(dict.get('cellulareServizio')))
            p.aggiungi_numero_telefono(dict.get('cellulareServizio'), True)

        ASSOC_ID_PERSONE.update({int(id): p.pk})
        # print(dict.keys())

        cursore.close()

@transaction.atomic
def carica_appartenenze():
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, comitato, stato, timestamp, conferma, inizio, fine
        FROM
           appartenenza
        WHERE
                volontario IS NOT NULL
            AND comitato IS NOT NULL
            AND stato IS NOT NULL
            AND inizio IS NOT NULL
            AND timestamp IS NOT NULL
        """
    )
    apps = cursore.fetchall()
    totale = int(cursore.rowcount)

    contatore = 0

    for app in apps:

        contatore += 1

        id = int(app[0])

        if args.verbose:
            print("    - " + progresso(contatore, totale) + ": Appartenenza id=" + stringa(id))

        persona = int(app[1])
        comitato = int(app[2])

        if persona not in ASSOC_ID_PERSONE:
            if args.verbose:
                print("      IGNORATA: Persona non riconosciuta (id=" + stringa(persona) + ")")
            continue
        persona = ASSOC_ID_PERSONE[persona]
        persona = Persona.objects.get(pk=persona)

        if comitato not in ASSOC_ID_COMITATI['Comitato']:
            if args.verbose:
                print("      IGNORATA: Comitato non riconosciuto (id=" + stringa(comitato) + ")")
            continue
        comitato = ASSOC_ID_COMITATI['Comitato'][comitato][1]
        comitato = Sede.objects.get(pk=comitato)

        inizio = data_da_timestamp(app[6], None)
        fine = data_da_timestamp(app[7], None) if app[7] else None

        if inizio is None:
            if args.verbose:
                print("      IGNORATA: Non valida (inizio fuori range)")
            continue

        stato = int(app[3])

        """
        define('MEMBRO_DIMESSO',            0);
        define('MEMBRO_TRASFERITO',         1);
        define('MEMBRO_ORDINARIO_DIMESSO',  2);
        define('MEMBRO_APP_NEGATA',         3);
        define('MEMBRO_ORDINARIO_PROMOSSO', 4);
        define('MEMBRO_EST_TERMINATA',      5);
        define('MEMBRO_TRASF_ANN',          9);
        define('MEMBRO_TRASF_NEGATO',      10);
        define('MEMBRO_EST_ANN',           14);
        define('MEMBRO_EST_NEGATA',        15);
        define('MEMBRO_ORDINARIO',         16);
        define('SOGLIA_APPARTENENZE',      19);
        define('MEMBRO_TRASF_IN_CORSO',    20);
        define('MEMBRO_EST_PENDENTE',      25);
        define('MEMBRO_PENDENTE',          30);
        define('MEMBRO_ESTESO',            35);
        define('MEMBRO_VOLONTARIO',        40);
        define('MEMBRO_MODERATORE',        50);
        define('MEMBRO_DIPENDENTE',        60);
        define('MEMBRO_PRESIDENTE',        70);
        """

        ## Trasferimento ed Estensione in corso, non sono piu' stati validi.
        if stato in [20, 25]:
            if args.verbose:
                print("      IGNORATA: Appartenenza fittizia (trasferimento/estensione in corso)")
                # TODO Trasferimenti ed estensioni
            continue

        if stato in [5, 14, 15, 25, 35]:
            membro = Appartenenza.ESTESO

        elif stato in [0, 1, 3, 9, 10, 20, 30, 40, 50, 60, 70, 80]:
            membro = Appartenenza.VOLONTARIO

        elif stato in [2, 4, 16]:
            membro = Appartenenza.ORDINARIO
            comitato = comitato.superiore(REGIONALE)

        else:
            if args.verbose:
                print("      IGNORATA: Stato appartenenza non riconosciuto (stato=" + stringa(stato) + ")")
            continue

        # Motivo della terminazione

        terminazione = None

        if stato in [0, 2]:
            terminazione = Appartenenza.DIMISSIONE

        if stato == 1:
            terminazione = Appartenenza.TRASFERIMENTO

        if stato == 4:
            terminazione = Appartenenza.PROMOZIONE

        # Stato di conferma dell'appartenenza

        if stato in [0, 1, 2, 4, 5, 16, 35, 40, 50, 60, 70, 80]:
            confermata = True

        elif stato in [3, 9, 10, 14, 15]:
            confermata = False

        else:
            confermata = False  # MEMBRO_PENDENTE

        if args.verbose:
            print("      - Creazione appartenenza")

        # Creazione della nuova appartenenza
        a = Appartenenza(
            persona=persona,
            sede=comitato,
            inizio=inizio,
            fine=fine,
            confermata=confermata,
            membro=membro,
            terminazione=terminazione,
        )
        a.save()

        # Pendenti.
        if stato == 30:  # MEMBRO_PENDENTE
            if args.verbose:
                print("      - Pendente, richiesta autorizzazione")

            a.autorizzazione_richiedi(
                persona,
                ((PRESIDENTE, comitato.comitato),),
            )

        ASSOC_ID_APPARTENENZE.update({id: a.pk})

        # Terminati.
        # Non accettati.

    if args.verbose:
        print("  - Persisto su database...")
    return

def locazione(geo, indirizzo):
    if not indirizzo:
        return None
    try:
        l = Locazione.objects.get(indirizzo=indirizzo)
    except:
        l = Locazione(geo=geo, indirizzo=indirizzo)
        l.save()
    return l

def comitato_oid(oid):
    if not oid:
        return None
    oid = stringa(oid)
    oid = oid.split(':')
    if len(oid) < 2:
        return None
    try:
        return ASSOC_ID_COMITATI[oid[0]][int(oid[1])][0].objects.get(pk=ASSOC_ID_COMITATI[oid[0]][int(oid[1])][1])
    except:
        return None

def comitato_estensione(comitato, estensione):
    if not comitato:
        return False
    if estensione is None:
        return comitato
    estensione = int(estensione)
    if estensione == 90:
        return None
    esteso = comitato
    while True:
        if esteso.estensione == COMITATO_ESTENSIONE_COSTANTE[estensione]:
            return esteso
        if esteso.genitore is None:
            return comitato
        esteso = esteso.genitore

def persona_id(id):
    if not id:
        return None
    id = int(id)
    try:
        return Persona.objects.get(pk=ASSOC_ID_PERSONE[id])
    except:
        return None

def area_id(id):
    if not id:
        return None
    id = int(id)
    try:
        return Area.objects.get(pk=ASSOC_ID_AREE[id])
    except:
        return None

def attivita_id(id):
    if not id:
        return None
    try:
        id = int(id)
        return Attivita.objects.get(pk=ASSOC_ID_ATTIVITA[id])
    except:
        return None

def turno_id(id):
    if not id:
        return None
    id = int(id)
    try:
        return Turno.objects.get(pk=ASSOC_ID_TURNI[id])
    except:
        return None

def carica_comitato(posizione=True, tipo='nazionali', id=1, ref=None, num=0):

    comitato = ottieni_comitato(tipo, id)

    if 'principale' in comitato and int(comitato['principale']) == 1:
        ASSOC_ID_COMITATI[COMITATO_OID[tipo]].update({id: (Sede, ref.pk)})
        c = ref

    else:

        c = Sede(
            genitore=ref,
            nome=stringa(comitato['nome']),
            tipo=Sede.COMITATO,
            estensione=COMITATO_ESTENSIONE[tipo],
            vecchio_id=int(id),
        )
        c.save()

        ASSOC_ID_COMITATI[COMITATO_OID[tipo]].update({id: (Sede, c.pk)})

    if posizione and 'formattato' in comitato['dati'] and comitato['dati']['formattato']:
        c.imposta_locazione(stringa(comitato['dati']['formattato']))

    if 'telefono' in comitato['dati'] and comitato['dati']['telefono']:
        c.telefono = parse_numero(comitato['dati']['telefono'])
        c.save()

    if 'fax' in comitato['dati'] and comitato['dati']['fax']:
        c.fax = parse_numero(comitato['dati']['fax'])
        c.save()

    if 'email' in comitato['dati'] and comitato['dati']['email']:
        c.email = comitato['dati']['email']
        c.save()

    if args.verbose:
        print("    - " + ("-"*num) + " " + c.nome + ": " + stringa(c.locazione))

    totale = 1
    for (a, b) in ottieni_figli(tipo,id):
        totale += carica_comitato(posizione, a, b, c, num+1)

    return totale

@transaction.atomic
def carica_comitati(geo):
    with Sede.objects.delay_mptt_updates():
        n = carica_comitato(geo)
        print("  - Persisto su database...")
    return n

def carica_deleghe():
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, comitato, estensione, volontario, applicazione, dominio, inizio, fine, pConferma, tConferma,
            partecipazione
        FROM
            delegati
        WHERE   comitato IS NOT NULL
            AND comitato <> ''
            AND volontario IS NOT NULL
            AND volontario <> ''
            AND inizio IS NOT NULL
            AND inizio <> ''
        """
    )
    deleghe = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for delega in deleghe:

        contatore += 1

        id = int(delega[0])
        sede = comitato_oid(delega[1])
        persona = persona_id(delega[3])

        if args.verbose:
            print("    - " + progresso(contatore, totale) + "Delega: id=%s, sede=%s, persona=%s" %
                  (id, str(sede.pk) if sede else None, persona.codice_fiscale if persona else None))


        tipo = int(delega[4])
        if tipo == 30:
            tipo = PRESIDENTE
        elif tipo == 40:
            if not delega[5]:
                if args.verbose:
                    print("      TIPO NON VALIDO (OBIETTIVO SENZA DOMINIO), SALTATA")
                continue

            ob = int(delega[5])
            if ob == 1:
                tipo = DELEGATO_OBIETTIVO_1
            elif ob == 2:
                tipo = DELEGATO_OBIETTIVO_2
            elif ob == 3:
                tipo = DELEGATO_OBIETTIVO_3
            elif ob == 4:
                tipo = DELEGATO_OBIETTIVO_4
            elif ob == 5:
                tipo = DELEGATO_OBIETTIVO_5
            elif ob == 6:
                tipo = DELEGATO_OBIETTIVO_6
            else:
                raise ValueError("Delegato non valido ob=%d" % (ob, ))
        elif tipo == 50:
            tipo = DELEGATO_CO
        elif tipo == 60:
            if delega[10] is not None:  # Se delega per Partecipazione
                tipo = UFFICIO_SOCI_TEMPORANEO
            else:
                tipo = UFFICIO_SOCI
        elif tipo == 70:
            tipo = RESPONSABILE_PATENTI
        elif tipo == 80:
            tipo = RESPONSABILE_FORMAZIONE
        elif tipo == 90:
            tipo = RESPONSABILE_AUTOPARCO
        elif tipo == 100:
            tipo = RESPONSABILE_DONAZIONI
        else:
            raise ValueError("Tipo delegato non valido tipo=%d" % (tipo,))

        inizio = data_da_timestamp(delega[6], None)
        fine = data_da_timestamp(delega[7], None)
        firmatario = persona_id(delega[8])
        creazione = data_da_timestamp(delega[9])


        if not sede:
            if args.verbose:
                print("      COMITATO NON VALIDO, SALTATA")
            continue

        if not persona:
            if args.verbose:
                print("      PERSONA NON VALIDA, SALTATA")
            continue

        if not inizio:
            if args.verbose:
                print("      INIZIO NON VALIDO, SALTATA")
            continue

        if args.verbose:
            print("      - Creazione delega")

        d = Delega(
            persona=persona,
            tipo=tipo,
            oggetto=sede,
            inizio=inizio,
            fine=fine,
            firmatario=firmatario,
            creazione=creazione,
        )
        d.save()

        ASSOC_ID_DELEGHE.update({id: d.pk})




def carica_aree():
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, nome, comitato, responsabile, obiettivo
        FROM
            aree
        WHERE   comitato IS NOT NULL
            AND comitato <> ''
            AND responsabile IS NOT NULL
            AND responsabile <> ''
            AND obiettivo IS NOT NULL
            AND obiettivo IN (1, 2, 3, 4, 5, 6)
        """
    )
    aree = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for area in aree:

        contatore += 1

        id = int(area[0])
        nome = stringa(area[1])
        comitato = comitato_oid(area[2])
        responsabile = persona_id(area[3])
        obiettivo = int(area[4])

        if args.verbose:
            print("    - " + progresso(contatore, totale) + "Area: id=%s, comitato=%s, obiettivo=%d" % (id, area[2], obiettivo))

        if not comitato:
            if args.verbose:
                print("      COMITATO NON VALIDO, SALTATO")
            continue

        if not responsabile:
            if args.verbose:
                print("      RESPONSABILE NON VALIDO, SALTATO (id=%s)" % (area[3],))
            continue

        # Se esiste una area uguale (solo aggiunta responsabile)
        if args.verbose:
            print("      - Ricerca aree da accorpare...")

        esistente = Area.objects.filter(nome=nome, sede=comitato, obiettivo=obiettivo)
        if esistente.exists():
            esistente = esistente[0]

            if args.verbose:
                print("        - Trovata area, id=%d, nome=%s" % (esistente.pk, esistente.nome))
                print("      - Aggiunta delegato, persona=%s" % (stringa(responsabile), ))

            esistente.aggiungi_delegato(DELEGATO_AREA, responsabile)

            ASSOC_ID_AREE[id] = esistente.pk
            continue

        if args.verbose:
            print("      - Aggiunta della nuova area")
        a = Area(sede=comitato, obiettivo=obiettivo, nome=nome,)
        a.save()

        if args.verbose:
            print("      - Aggiunta del responsabile")
        a.aggiungi_delegato(DELEGATO_AREA, responsabile)

        ASSOC_ID_AREE[id] = a.pk

    cursore.close()

@transaction.atomic
def carica_attivita():

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, nome, luogo, comitato, visibilita, referente, tipo, descrizione, stato, area, apertura
        FROM
            attivita
        WHERE   nome IS NOT NULL
            AND comitato IS NOT NULL
            AND comitato <> ''
            AND area IS NOT NULL
        """
    )
    attivita = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for att in attivita:

        contatore += 1

        id = int(att[0])
        nome = stringa(att[1])
        luogo = stringa(att[2])
        comitato = comitato_oid(att[3])
        estensione = comitato_estensione(comitato, int(att[4]))
        referente = persona_id(att[5])
        descrizione = stringa(att[7])
        if descrizione is None:
            descrizione = ''
        stato = Attivita.BOZZA if int(att[8]) == 10 else Attivita.VISIBILE
        area = area_id(att[9])

        if att[10] is None:
            apertura = Attivita.CHIUSA
        else:
            apertura = Attivita.APERTA if int(att[10]) == 10 else Attivita.CHIUSA

        if args.verbose:
            print("    - " + progresso(contatore, totale) + "Attivita: id=%s, comitato=%s, nome=%s" % (id, stringa(att[3]), stringa(nome)))

        if not comitato:
            if args.verbose:
                print("      COMITATO NON VALIDO, SALTATO")
            continue

        if not area:
            if args.verbose:
                print("      AREA NON VALIDA, SALTATA")
            continue

        if args.verbose:
            print("      - Creazione attivita'")

        a = Attivita(
            sede=comitato,
            estensione=estensione,
            nome=nome,
            descrizione=descrizione,
            area=area,
            apertura=apertura,
            stato=stato,
            vecchio_id=int(id),
        )
        a.save()

        if luogo and args.geo:
            l = a.imposta_locazione(luogo)
            if args.verbose:
                print("      - Impostato luogo: " + stringa(l))

        if referente:
            a.aggiungi_delegato(REFERENTE, referente)
            if args.verbose:
                print("      - Impostato referente: " + stringa(referente.codice_fiscale))

        ASSOC_ID_ATTIVITA[id] = a.pk

    cursore.close()

def carica_turni():
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, attivita, nome, inizio, fine, timestamp, minimo, massimo, prenotazione
        FROM
            turni
        WHERE   attivita IS NOT NULL
            AND attivita <> ''
            AND inizio IS NOT NULL
            AND inizio <> ''
            AND fine IS NOT NULL
            AND fine <> ''
        """
    )
    turni = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for turno in turni:
        contatore += 1

        id = int(turno[0])
        attivita = attivita_id(turno[1])
        nome = stringa(turno[2])
        if not nome:
            nome = '(Turno senza nome)'
        inizio = data_da_timestamp(turno[3], None)
        fine = data_da_timestamp(turno[4], None)
        creazione = data_da_timestamp(turno[5])
        minimo = int(turno[6])
        massimo = int(turno[7]) if int(turno[7]) != 999 else None
        prenotazione = data_da_timestamp(turno[8], inizio)

        if args.verbose:
            print("    - " + progresso(contatore, totale) + "Turno id=%d, attivita=%s" % (id, stringa(attivita.pk) if attivita else None,))

        if not attivita:
            if args.verbose:
                print("      ATTIVITA NON VALIDA, SALTATO")
            continue

        if inizio is None or fine is None:
            if args.verbose:
                print("      INIZIO O FINE NON VALIDI, SALTATO")
            continue

        if args.verbose:
            print("      - Creazione turno")

        t = Turno(
            attivita=attivita,
            nome=nome,
            inizio=inizio,
            fine=fine,
            creazione=creazione,
            minimo=minimo,
            massimo=massimo,
            prenotazione=prenotazione,
        )
        t.save()

        ASSOC_ID_TURNI.update({id: t.pk})


@transaction.atomic
def carica_partecipazioni():

    # Dizionario per le autorizzazioni. Es:
    #  AUTORIZZAZIONI[PART_ID] = [(...), (...)]
    AUTORIZZAZIONI = {}

    print("  - Caricamento autorizzazioni in memoria")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, partecipazione, timestamp, pFirma, tFirma, note, stato, motivo
        FROM
            autorizzazioni
        WHERE   volontario IS NOT NULL
            AND volontario <> ''
            AND partecipazione IS NOT NULL
            AND partecipazione <> ''
            AND stato IS NOT NULL
        """
    )
    auts = cursore.fetchall()
    for aut in auts:
        part = int(aut[2])
        try:
            AUTORIZZAZIONI[part] += [aut]
        except KeyError:
            AUTORIZZAZIONI.update({part: [aut]})

    cursore.close()

    print("  - Scaricamento partecipazioni")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, turno, stato, tipo, timestamp, tConferma, pConferma
        FROM
            partecipazioni
        WHERE   volontario IS NOT NULL
            AND volontario <> ''
            AND turno IS NOT NULL
            AND turno <> ''
        """
    )
    parts = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for part in parts:
        contatore += 1

        id = int(part[0])
        persona = persona_id(part[1])
        turno = turno_id(part[2])
        stato_raw = int(part[3])
        if stato_raw == 0:
            stato = Partecipazione.RITIRATA
        else:
            stato = Partecipazione.RICHIESTA
        creazione = data_da_timestamp(part[5])
        tConferma = data_da_timestamp(part[6], None)
        pConferma = persona_id(part[7])

        if args.verbose:
            print("    - " + progresso(contatore, totale) + "Partecipazione id=%d, turno=%s" % (id, part[2],))

        if not persona:
            if args.verbose:
                print("      PERSONA PARTECIPANTE NON VALIDA, SALTATA")
            continue

        if not turno:
            if args.verbose:
                print("      TURNO NON VALIDO, SALTATA")
            continue

        if args.verbose:
            print("      - Creazione partecipazione")

        p = Partecipazione(
            persona=persona,
            turno=turno,
            stato=stato,
            ritirata=True if stato_raw == 0 else False,
            confermata=False if stato_raw == 20 else True,
            creazione=creazione,
        )
        p.save()

        ASSOC_ID_PARTECIPAZIONI[id] = p.pk

        try:
            auts = AUTORIZZAZIONI[id]
        except KeyError:
            auts = []

        if args.verbose:
            print("      - %d autorizzazioni da creare" % (len(auts),))

        progressivo = 0

        for aut in auts:

            progressivo += 1
            # id, volontario, partecipazione, timestamp, pFirma, tFirma, note, stato, motivo

            richiedente = persona
            firmatario = persona_id(aut[1])
            creazione = data_da_timestamp(aut[3])
            ultima_modifica = data_da_timestamp(aut[5])
            stato = int(aut[7])
            concessa = True if stato == 30 else False if stato == 20 else None

            if stato == 10 and turno.prenotazione < datetime.now():  # pendente e troppo tardi...
                if args.verbose:
                    print("      - Troppo tardi per prenotarsi, pendente ignorata")
                    print("        Cancello autorizzazioni associate...")
                Autorizzazione.objects.filter(
                    richiedente=richiedente,
                    oggetto_tipo=ContentType.objects.get_for_model(Partecipazione),
                    oggetto_id=p.pk
                ).delete()
                p.stato = Partecipazione.RITIRATA
                p.save()
                break

            necessaria = True

            # A chi e' stata rivolta la richiesta? Mica al Presidente del MIO comitato?
            if firmatario.deleghe_attuali(al_giorno=creazione, tipo=PRESIDENTE).exists():
                # Presidente del mio comitato, assumo seconda.
                destinatario_ruolo = PRESIDENTE
                try:
                    destinatario_oggetto = Sede.objects\
                    .get(
                        Appartenenza.objects.attuale(al_giorno=creazione).via("appartenenza"),
                        appartenenza__persona=richiedente, membro__in=[Appartenenza.VOLONTARIO, Appartenenza.ESTESO]
                    )
                except:
                    if args.verbose:
                        print("      - Sembra come richiesta al presidente, ma nessuna appartenenza, quindi Sede")
                        continue

            else:
                # Referente dell'attivita'
                destinatario_ruolo = REFERENTE
                destinatario_oggetto = turno.attivita


            necessaria = False
            motivo_negazione = '' if not aut[8] else stringa(aut[8])

            a = Autorizzazione(
                richiedente=richiedente,
                firmatario=firmatario,
                concessa=concessa,
                motivo_negazione=motivo_negazione,
                oggetto=p,
                necessaria=necessaria,
                progressivo=progressivo,
                destinatario_ruolo=destinatario_ruolo,
                destinatario_oggetto=destinatario_oggetto,
                creazione=creazione,
                ultima_modifica=ultima_modifica,
            )
            a.save()


def carica_tesseramenti():
    print("  - Caricamento dei Tesseramenti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, stato, inizio, fine, anno, attivo, ordinario, benemerito
        FROM
            tesseramenti
        """
    )
    tesseramenti = cursore.fetchall()

    for tesseramento in tesseramenti:
        id = int(tesseramento[0])
        stato = Tesseramento.APERTO if int(tesseramento[1]) == 10 else Tesseramento.CHIUSO
        inizio = data_da_timestamp(tesseramento[2])
        anno = int(tesseramento[4])
        quota_attivo = float(tesseramento[5])
        quota_ordinario = float(tesseramento[6])
        quota_benemerito = float(tesseramento[7])

        print("    - %d: %f eur attivo, %f eur ordinario, %f eur benemerito" % (anno, quota_attivo, quota_ordinario, quota_benemerito))

        t = Tesseramento(
            anno=anno,
            stato=stato,
            inizio=inizio,
            quota_attivo=quota_attivo,
            quota_ordinario=quota_ordinario,
            quota_benemerito=quota_benemerito,
        )
        t.save()

        ASSOC_ID_TESSERAMENTI[id] = t.pk

    cursore.close()


def carica_quote():
    print("  - Caricamento delle Quote...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        quote.id, quote.appartenenza, appartenenza.volontario, appartenenza.comitato,
        quote.timestamp, quote.tConferma, quote.pConferma, quote.quota,
        quote.causale, quote.offerta, quote.anno, quote.pAnnullata, quote.tAnnullata,
        quote.progressivo, quote.benemerito

        FROM
        quote INNER JOIN appartenenza
            ON quote.appartenenza = appartenenza.id
        INNER JOIN anagrafica
            ON quote.pConferma = anagrafica.id
        INNER JOIN anagrafica AS a2
            ON appartenenza.volontario = a2.id


        WHERE
        quote.quota IS NOT NULL       	AND
        quote.anno IS NOT NULL        	AND
        quote.timestamp IS NOT NULL   	AND
        quote.causale IS NOT NULL 		AND
        quote.progressivo IS NOT NULL   AND
        appartenenza.comitato IS NOT NULL
    """)
    quote = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for quota in quote:
        contatore += 1
        id = int(quota[0])

        try:
            appartenenza_id = ASSOC_ID_APPARTENENZE[int(quota[1])]

        except KeyError:
            print("   - Quota Saltata (%d) appartenenza non esistente (%d)" % (
                id, int(quota[1]),
            ))
            continue

        #print("Persona: %d, %d" % (int(quota[2]), ASSOC_ID_PERSONE[int(quota[2])]))
        persona = Persona.objects.get(pk=ASSOC_ID_PERSONE[int(quota[2])])

        try:
            sede = Sede.objects.get(pk=ASSOC_ID_COMITATI["Comitato"][int(quota[3])][1]).comitato

        except KeyError:
            print("   - Quota Saltata (%d) comitato non esistente (%d)" % (
                id, int(quota[3]),
            ))
            continue

        data_versamento = data_da_timestamp(quota[4], data_da_timestamp(quota[5]))
        data_creazione = data_da_timestamp(quota[5])
        registrato_da = ASSOC_ID_PERSONE[int(quota[6])]

        importo = float(quota[7])

        causale = stringa(quota[8]) or ''
        causale_extra = stringa(quota[9]) or ''
        anno = int(quota[10])

        annullato_da = ASSOC_ID_PERSONE[int(quota[11])] if quota[11] else None
        data_annullamento = data_da_timestamp(quota[12], data_creazione)

        stato = Quota.REGISTRATA if annullato_da is None else Quota.ANNULLATA

        progressivo = int(quota[13])

        tesseramento = Tesseramento.objects.get(anno=anno)
        da_pagare = tesseramento.importo_da_pagare(persona)
        importo_extra = 0.0

        if importo > da_pagare:
            importo_extra = importo - da_pagare
            importo = da_pagare

        print("   - %s: Quota, sede=%d, numero=%d/%d" %
              (progresso(contatore, totale), sede.pk,
               progressivo, anno,))

        try:
            q = Quota(
                appartenenza_id=appartenenza_id,
                persona=persona,
                sede=sede,
                progressivo=progressivo,
                anno=anno,
                data_versamento=data_versamento,
                data_annullamento=data_annullamento,
                registrato_da_id=registrato_da,
                annullato_da_id=annullato_da,
                stato=stato,
                importo=importo,
                importo_extra=importo_extra,
                causale=causale,
                causale_extra=causale_extra,
            )
            q.save()

        except IntegrityError:
            print("     - id=%d QUOTA DUPLICATA SALTATA" % (id, ))
            continue

        ASSOC_ID_QUOTE[id] = q.pk

    cursore.close()

@transaction.atomic
def carica_titoli():
    print("  - Caricamento dei Titoli e Patenti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        id, nome, tipo
        FROM titoli
        WHERE nome IS NOT NULL
        AND nome <> ''
        """
    )
    titoli = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for titolo in titoli:
        contatore += 1
        id = int(titolo[0])
        nome = stringa(titolo[1])
        tipon = int(titolo[2])

        if tipon == 0:
            tipo = Titolo.COMPETENZA_PERSONALE
            richiede_conferma = False
            richiede_data_ottenimento = False
            richiede_luogo_ottenimento = False
            richiede_data_scadenza = False
            richiede_codice = False
            inseribile_in_autonomia = True

        elif tipon == 1:
            tipo = Titolo.PATENTE_CIVILE
            richiede_conferma = False
            richiede_data_ottenimento = True
            richiede_luogo_ottenimento = True
            richiede_data_scadenza = True
            richiede_codice = True
            inseribile_in_autonomia = True

        elif tipon == 2:
            tipo = Titolo.PATENTE_CRI
            richiede_conferma = True
            richiede_data_ottenimento = True
            richiede_luogo_ottenimento = True
            richiede_data_scadenza = True
            richiede_codice = True
            inseribile_in_autonomia = True

        elif tipon == 3:
            tipo = Titolo.TITOLO_STUDIO
            richiede_conferma = False
            richiede_data_ottenimento = True
            richiede_luogo_ottenimento = True
            richiede_data_scadenza = True
            richiede_codice = True
            inseribile_in_autonomia = True

        elif tipon == 4:
            tipo = Titolo.TITOLO_CRI
            richiede_conferma = True
            richiede_data_ottenimento = True
            richiede_luogo_ottenimento = True
            richiede_data_scadenza = True
            richiede_codice = True
            inseribile_in_autonomia = True

        else:
            raise ValueError("Tipo non riconosciuto: %d" % (tipon, ))

        print(" - %s, titolo nome='%s' tipo=%s" % (progresso(contatore,totale), nome, tipo,))
        t = Titolo(
            nome=nome,
            vecchio_id=id,
            tipo=tipo,
            richiede_conferma=richiede_conferma,
            richiede_data_ottenimento=richiede_data_ottenimento,
            richiede_luogo_ottenimento=richiede_luogo_ottenimento,
            richiede_data_scadenza=richiede_data_scadenza,
            richiede_codice=richiede_codice,
            inseribile_in_autonomia=inseribile_in_autonomia,
        )
        t.save()

        ASSOC_ID_TITOLI[id] = t.pk

    cursore.close()

@transaction.atomic
def carica_titoli_personali():

    print("  - Caricamento dei Titoli e Patenti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        titoliPersonali.id, titoliPersonali.volontario, titoliPersonali.titolo,
        titoliPersonali.inizio, titoliPersonali.fine, titoliPersonali.luogo,
        titoliPersonali.codice, titoliPersonali.corso, titoliPersonali.tConferma,
        titoliPersonali.pConferma
        FROM titoliPersonali INNER JOIN anagrafica ON
            titoliPersonali.volontario = anagrafica.id
        WHERE titoliPersonali.volontario IS NOT NULL
        AND titoliPersonali.titolo IS NOT NULL
        AND titoliPersonali.titolo IN (select id from titoli)
        AND (titoliPersonali.pConferma IS NULL
                OR titoliPersonali.pConferma IN (select id from anagrafica))

        """
    )
    titoli = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for titolo in titoli:
        contatore += 1
        id = int(titolo[0])

        try:
            persona = ASSOC_ID_PERSONE[int(titolo[1])]

        except KeyError:
            print("    - SALTATO Persona non trovata %d " % (int(titolo[1]),))
            continue

        titolo_id = ASSOC_ID_TITOLI[int(titolo[2])]
        inizio = data_da_timestamp(titolo[3], None)
        fine = data_da_timestamp(titolo[4], None)
        luogo = stringa(titolo[5])
        codice = stringa(titolo[6]) or None
        corso = stringa(titolo[7]) or None
        tConferma = data_da_timestamp(titolo[8], None)
        pConferma = ASSOC_ID_PERSONE[int(titolo[9])] if titolo[9] else None

        print("   - %s, persona=%d, titolo=%d, tConferma=%s" % (
            progresso(contatore, totale), persona, titolo_id, tConferma
        ))

        t = TitoloPersonale(
            titolo_id=titolo_id,
            persona_id=persona,
            data_ottenimento=inizio,
            data_scadenza=fine,
            luogo_ottenimento=luogo,
            codice=codice,
            codice_corso=corso,
            certificato=True if corso else False,
            certificato_da_id=pConferma if corso else None,
        )
        t.save()

        ASSOC_ID_TITOLIPERSONALI[id] = t.pk

        if not pConferma:

            print("     - richiesta al presidente e us")
            persona = Persona.objects.get(pk=persona)

            sedi_attuali = persona.sedi_attuali()
            if not sedi_attuali:
                print("     - nessuna appartenenza, salto")
                continue
            sede = sedi_attuali[0].comitato

            t.autorizzazione_richiedi(
                persona,
                (
                    (PRESIDENTE, sede),
                    (UFFICIO_SOCI, sede),
                )
            )

        else:

            print("     - autorizzazione firmata")
            a = Autorizzazione(
                oggetto=t,
                richiedente_id=persona,
                firmatario_id=pConferma,
                concessa=True,
                destinatario_ruolo=PRESIDENTE,
                destinatario_oggetto=t,
            )
            a.save()

    cursore.close()


def carica_sangue_sedi():
    print("  - Caricamento delle sedi di donazione sangue...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        id, citta, provincia, regione, nome
        FROM
        donazioni_sedi
        """
    )
    sedi = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for sede in sedi:
        contatore += 1
        id = int(sede[0])
        citta = stringa(sede[1])
        provincia = stringa(sede[2])
        regione = stringa(sede[3])
        nome = stringa(sede[4])

        s = sangue.Sede(
            citta=citta,
            provincia=provincia,
            regione=regione,
            nome=nome,
        )
        print("    - %s: Sede %s" % (
            progresso(contatore, totale), str(s),
        ))
        s.save()

        ASSOC_ID_SANGUE_SEDI[id] = s.pk

    cursore.close()


@transaction.atomic
def carica_sangue_donatori():
    print("  - Caricamento dei donatori di sangue...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        id, volontario, sangue_gruppo, fattore_rh, fanotipo_rh, kell, codice_sit, sede_sit
        FROM
        donazioni_anagrafica
        """
    )
    donatori = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for donatore in donatori:
        contatore += 1

        id = int(donatore[0])

        try:
            persona_id = ASSOC_ID_PERSONE[int(donatore[1])]

        except KeyError:
            print("   - Profilo saltato, persona non trovata, donatore id=%d, persona=%d" % (
                id, int(donatore[1])
            ))
            continue  # Persona non trovata - profilo saltato.

        sangue_gruppo = int(donatore[2])
        sangue_gruppo = {
            1: sangue.Donatore.GRUPPO_0,
            2: sangue.Donatore.GRUPPO_A,
            3: sangue.Donatore.GRUPPO_B,
            4: sangue.Donatore.GRUPPO_AB,
        }[sangue_gruppo]

        fattore_rh = int(donatore[3])
        fattore_rh = {
            0: None,
            1: sangue.Donatore.RH_POS,
            2: sangue.Donatore.RH_NEG,
        }[fattore_rh]

        fanotipo_rh = int(donatore[4])
        fanotipo_rh = [
            None,
            'CCDee',
            'ccDEE',
            'CcDee',
            'ccDEe',
            'ccDee',
            'CCDEE',
            'CCDEe',
            'CcDEE',
            'CcDEe',
            'Ccddee',
            'CCddee',
            'ccddEe',
            'ccddEE',
            'ccddee',
            'CcddEe',
        ][fanotipo_rh]

        kell = int(donatore[5])
        kell = [
            None,
            'K+k+',
            'K+k-',
            'K-k+',
            'Kp(a+b+)',
            'Kp(a-b+)',
        ][kell]

        codice_sit = stringa(donatore[6])
        if codice_sit == "0":
            codice_sit = None

        sede_sit = int(donatore[7])
        if sede_sit == 0:
            sede_sit = None

        else:
            sede_sit = ASSOC_ID_SANGUE_SEDI[sede_sit]

        d = sangue.Donatore(
            persona_id=persona_id,
            gruppo_sanguigno=sangue_gruppo,
            fattore_rh=fattore_rh,
            fanotipo_rh=fanotipo_rh,
            kell=kell,
            codice_sit=codice_sit,
            sede_sit_id=sede_sit,
        )
        print("    - %s: Donatore %s" % (
            progresso(contatore, totale), str(d),
        ))

        d.save()
        ASSOC_ID_SANGUE_DONATORI[id] = d.pk

    cursore.close()


def carica_sangue_meriti():
    print("  - Caricamento dei meriti di donazione...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        id, volontario, donazione, merito
        FROM
        donazioni_merito
        """
    )

    meriti = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for merito in meriti:
        contatore += 1

        id = int(merito[0])
        try:
            persona_id = ASSOC_ID_PERSONE[int(merito[1])]

        except KeyError:
            print("    - Persona id=%d non esistente, merito saltato" % (int(merito[1]),))
            continue

        merito = stringa(merito[2])

        print("    - %s: Merito id=%d" % (
            progresso(contatore, totale), id,
        ))


        m = sangue.Merito(
            persona_id=persona_id,
            merito=merito,
        )
        m.save()

        ASSOC_ID_SANGUE_MERITI[id] = m.pk

    cursore.close()


def carica_sangue_donazioni():
    print("  - Caricamento delle donazioni di sangue...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
        id, volontario, donazione, data, luogo, tConferma, pConferma
        FROM
        donazioni_personale
        WHERE
        data IS NOT NULL
        """
    )

    donazioni = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for donazione in donazioni:
        contatore += 1

        id = int(donazione[0])
        try:
            persona_id = ASSOC_ID_PERSONE[int(donazione[1])]

        except KeyError:
            print("    - Persona id=%d non esistente, donazione saltata" % (int(donazione[1]),))
            continue

        tipo = {
            '1':    'DD',
            '2':    'SI',
            '3':    'PL',
            '4':    'PP',
            '5':    'PI',
            '6':    'EP',
            '7':    '2R',
            '8':    '2P',
            '10':   'RP',
            '11':   'MO',
        }[stringa(donazione[2])]

        data = date.fromtimestamp(int(donazione[3]))
        luogo = ASSOC_ID_SANGUE_SEDI[int(donazione[4])] if donazione[4] else None

        tConferma = data_da_timestamp(int(donazione[5]), None) if donazione[5] else None
        pConferma = ASSOC_ID_PERSONE[int(donazione[6])] if donazione[6] else None

        d = sangue.Donazione(
            tipo=tipo,
            persona_id=persona_id,
            data=data,
            sede_id=luogo,
        )
        d.save()

        print("    - %s: Donazione id=%d" % (
            progresso(contatore, totale), id,
        ))


        if tConferma:
            a = Autorizzazione(
                richiedente_id=persona_id,
                firmatario_id=pConferma,
                concessa=True,
                oggetto=d,
                destinatario_ruolo=PRESIDENTE,
                destinatario_oggetto=d,
            )
            a.save()

        else:
            persona = Persona.objects.get(pk=persona_id)

            try:
                sede = persona.sedi_attuali()[0].comitato

            except:
                d.delete()
                continue

            d.autorizzazione_richiedi(
                persona,
                (
                    (PRESIDENTE, sede),
                    (UFFICIO_SOCI, sede)
                )
            )

        ASSOC_ID_SANGUE_DONAZIONI[id] = d.pk

    cursore.close()


def carica_commenti():

    print("  - Caricamento dei commenti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, attivita, commento, volontario, tCommenta
        FROM commenti
        WHERE commento IS NOT NULL
        """
    )

    commenti = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for commento in commenti:
        contatore += 1

        id = int(commento[0])
        try:
            attivita_id = ASSOC_ID_ATTIVITA[int(commento[1])]

        except KeyError:
            print("    - SALTATO Attivita id=%d non esistente, commento saltato" % (int(commento[1]),))
            continue

        except ValueError:
            print("    - SALTATO Attivita id=%s non valida, commento saltato" % (commento[1],))
            continue

        try:
            persona_id = ASSOC_ID_PERSONE[int(commento[3])]

        except KeyError:
            print("    - SALTATO Persona id=%d non esistente, commento saltato" % (int(commento[3]),))
            continue

        testo = stringa(commento[2])
        creazione = data_da_timestamp(commento[4])

        print("    - %s: Commento id=%d" % (
            progresso(contatore, totale), id,
        ))

        c = Commento(
            autore_id=persona_id,
            commento=testo,
            creazione=creazione,
            oggetto=Attivita.objects.get(pk=attivita_id)
        )
        c.save()

        ASSOC_ID_COMMENTI[id] = c.pk

    cursore.close()


def carica_corsibase():

    print("  - Caricamento dei corsi base...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, luogo, organizzatore,
            direttore, inizio, progressivo,
            anno, descrizione, stato,
            aggiornamento, tEsame
        FROM corsibase
        """
    )

    corsi = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for corso in corsi:
        contatore += 1

        id = int(corso[0])

        luogo = stringa(corso[1])

        organizzatore = comitato_oid(stringa(corso[2]))

        if not organizzatore:
            print("    - SALTATO Organizzatore non esistente (%s)" % (stringa(corso[2]), ))
            continue

        data_inizio = data_da_timestamp(corso[4])
        progressivo = int(corso[5])
        anno = int(corso[6])
        descrizione = stringa(corso[7]) or ''
        stato = int(corso[8])

        if stato == 0:
            stato = formazione.CorsoBase.ANNULLATO

        elif stato == 10:
            stato = formazione.CorsoBase.PREPARAZIONE

        elif stato == 20:
            stato = formazione.CorsoBase.TERMINATO

        elif stato == 30:
            stato = formazione.CorsoBase.ATTIVO

        else:
            raise ValueError("Valore non aspettato per corso base")

        aggiornamento = data_da_timestamp(corso[9])
        data_esame = data_da_timestamp(corso[10])

        print("    - %s: Corso base id=%d, num=%d/%d" % (
            progresso(contatore, totale), id, progressivo, anno
        ))

        c = formazione.CorsoBase(
            sede=organizzatore,
            data_inizio=data_inizio,
            data_esame=data_esame,
            creazione=min(data_inizio, aggiornamento),
            ultima_modifica=aggiornamento,
            descrizione=descrizione,
            progressivo=progressivo,
            anno=anno,
            stato=stato,
        )
        c.save()

        try:
            direttore_id = ASSOC_ID_PERSONE[int(corso[3])]
            direttore = Persona.objects.get(pk=direttore_id)
            print("      - Associo direttore %s" % (
                direttore_id.codice_fiscale,
            ))
            c.aggiungi_delegato(
                DIRETTORE_CORSO,
                direttore,
                inizio=c.creazione,
            )

        except:

            # OK Nessun direttore
            pass

        if args.geo and luogo:
            print("      - Imposto locazione %s" % (
                luogo,
            ))
            c.imposta_locazione(luogo)

        ASSOC_ID_CORSIBASE[id] = c.pk

    cursore.close()


def carica_corsibase_lezioni():

    print("  - Caricamento delle lezioni ai corsi base...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, nome, inizio, fine, corso
        FROM
            lezioni
        WHERE
            inizio IS NOT NULL AND fine IS NOT NULL
            AND corso IS NOT NULL
        """
    )

    lezioni = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for lezione in lezioni:
        contatore += 1

        id = int(lezione[0])
        nome = stringa(lezione[1])

        inizio = data_da_timestamp(lezione[2])
        fine = data_da_timestamp(lezione[3])

        try:
            corso = ASSOC_ID_CORSIBASE[int(lezione[4])]

        except IndexError:
            print ("    - SALTATO corso non trovato id=%d" % (int(lezione[4]),))
            continue

        print("    - %s: Lezione id=%d, corso=%d" % (
            progresso(contatore, totale), id, int(lezione[4])
        ))

        l = formazione.LezioneCorsoBase(
            corso_id=corso,
            nome=nome,
            inizio=inizio,
            fine=fine,
        )
        l.save()

        ASSOC_ID_CORSIBASE_LEZIONI[id] = l.pk

    cursore.close()


def carica_corsibase_assenze():

    print("  - Caricamento delle assenze alle lezioni ai corsi base...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, lezione, utente, pConferma, tConferma
        FROM
            lezioni_assenza
        """
    )

    assenze = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for assenza in assenze:
        contatore += 1

        id = int(assenza[0])

        try:
            lezione_id = ASSOC_ID_CORSIBASE_LEZIONI[int(assenza[1])]
        except KeyError:
            print("    - SALTATO Lezione id=%d non esistente" % (int(assenza[1]),))
            continue

        try:
            persona_id = ASSOC_ID_PERSONE[int(assenza[2])]
        except KeyError:
            print("    - SALTATO Persona id=%d non esistente" % (int(assenza[2]),))
            continue

        try:
            registrato_da_id = ASSOC_ID_PERSONE[int(assenza[3])]
        except KeyError:
            print("    - SALTATO Registrato da Persona id=%d non esistente" % (int(assenza[3]),))
            continue

        tConferma = data_da_timestamp(assenza[4])

        print("    - %s: Assenza id=%d, lezione=%d" % (
            progresso(contatore, totale), id, lezione_id,
        ))

        a = formazione.AssenzaCorsoBase(
            lezione_id=lezione_id,
            persona_id=persona_id,
            registrato_da_id=registrato_da_id,
            creazione=tConferma,
            ultima_modifica=tConferma,
        )
        a.save()

        ASSOC_ID_CORSIBASE_ASSENZE[id] = a.pk

    cursore.close()


def carica_aspiranti():

    print("  - Caricamento degli aspiranti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            aspiranti.id, aspiranti.data, aspiranti.utente, aspiranti.luogo
        FROM
            aspiranti
        INNER JOIN anagrafica ON aspiranti.utente = anagrafica.id
        """
    )

    aspiranti = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for aspirante in aspiranti:
        contatore += 1

        id = int(aspirante[0])

        data = data_da_timestamp(aspirante[1])
        luogo = stringa(aspirante[3])

        try:
            persona_id = ASSOC_ID_PERSONE[int(aspirante[2])]
        except KeyError:
            print("    - SALTATO Persona id=%d non esistente" % (int(aspirante[2]),))
            continue

        print("    - %s: Aspirante id=%d, persona=%d" % (
            progresso(contatore, totale), id, persona_id,
        ))

        a = formazione.Aspirante(
            persona_id=persona_id,
            creazione=data,
            ultima_modifica=data,
        )
        a.save()

        if args.geo:
            print("    - Impostazione locazione e calcola raggio: %s" % (luogo,))
            a.imposta_locazione(luogo)

        ASSOC_ID_ASPIRANTI[id] = a.pk

    cursore.close()


def carica_trasferimenti():


    print("  - Caricamento dei trasferimenti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, stato, appartenenza,
            volontario, protNumero, protData,
            motivo, negazione, timestamp,
            pConferma, tConferma, cProvenienza
        FROM
            trasferimenti
        """
    )

    trasferimenti = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for trasf in trasferimenti:
        contatore += 1

        id = int(trasf[0])

        stato = int(trasf[1])

        try:
            appartenenza_id = ASSOC_ID_APPARTENENZE[int(trasf[2])]
        except KeyError:
            print("    - SALTATO Appartenenza non trovata id=%d" % (int(trasf[2]),))
            continue

        appartenenza = Appartenenza.objects.get(pk=appartenenza_id)

        try:
            persona_id = ASSOC_ID_PERSONE[int(trasf[3])]
        except KeyError:
            print("    - SALTATO Persona non trovata id=%d" % (int(trasf[3])))
            continue

        protocollo_numero = stringa(trasf[4]) if trasf[4] else None
        protocollo_data = data_da_timestamp(trasf[5]) if trasf[5] else None

        motivo = stringa(trasf[6]) if trasf[6] else None
        motivo_negazione = stringa(trasf[7]) if trasf[7] else None

        creazione = data_da_timestamp(trasf[8])

        try:
            pConferma_id = ASSOC_ID_PERSONE[int(trasf[9])] if trasf[9] else None
        except KeyError:
            print("    - SALTATO Persona firmatario non trovata id=%d" % (int(trasf[9])))
            continue

        tConferma = data_da_timestamp(trasf[10]) if trasf[10] else None

        try:
            provenienza_id = ASSOC_ID_COMITATI['Comitato'][int(trasf[11])][1]

        except KeyError:
            print("    - SALTATO Comitato di provenienza non trovato id=%d" % (int(trasf[10]),))

        print("    - %s: Trasferimento id=%d, persona=%d, appartenenza=%d" % (
            progresso(contatore, totale), id, persona_id, appartenenza_id,
        ))

        precedente = Appartenenza.objects.filter(
            terminazione=Appartenenza.TRASFERIMENTO,
            persona_id=persona_id,
            sede_id=provenienza_id,
        )
        if precedente.exists():
            print("      - Aggiorna precedente appartenenza")
            appartenenza.precedente_id = precedente.first().pk
            appartenenza.save()

        t = Trasferimento(
            richiedente_id=persona_id,
            persona_id=persona_id,
            destinazione=appartenenza.sede,
            appartenenza=appartenenza,
            protocollo_numero=protocollo_numero,
            protocollo_data=protocollo_data,
            motivo=motivo,
            creazione=creazione,
            ultima_modifica=creazione,
            confermata=True if stato == 30 or stato == 40 else False,
        )
        t.save()

        if stato == 10:  # Trasferimento negato.
            a = Autorizzazione(
                oggetto=t,
                destinatario_ruolo=PRESIDENTE,
                destinatario_oggetto=Sede.objects.get(pk=provenienza_id),
                concessa=False,
                richiedente_id=persona_id,
                firmatario_id=pConferma_id,
                motivo_negazione=motivo_negazione,
                creazione=creazione,
                ultima_modifica=tConferma,
            )
            a.save()

        elif stato == 20:  # Trasferimento in corso.
            a = Autorizzazione(
                oggetto=t,
                destinatario_ruolo=PRESIDENTE,
                destinatario_oggetto=Sede.objects.get(pk=provenienza_id),
                concessa=None,
                richiedente_id=persona_id,
                creazione=creazione,
            )
            a.save()

        elif stato == 25:  # Annullata / Ritirata
            t.autorizzazioni_ritira()

        elif stato == 30 or stato == 40:  # OK!

            if stato == 40:  # Approvazione automatica
                t.protocollo_numero = t.PROTOCOLLO_AUTO
                t.save()

            else:  # Manuale, crea approvazione.
                a = Autorizzazione(
                    oggetto=t,
                    destinatario_ruolo=PRESIDENTE,
                    destinatario_oggetto=Sede.objects.get(pk=provenienza_id),
                    concessa=True,
                    richiedente_id=persona_id,
                    creazione=creazione,
                    ultima_modifica=tConferma,
                )
                a.save()

        else:
            raise ValueError("Valore stato non permesso %d" % (stato,))

        ASSOC_ID_TRASFERIMENTI[id] = t.pk

    cursore.close()





# Importazione dei Comitati

print("> Importazione dei Comitati")

if args.comitati:
    print("  - Eliminazione attuali")
    Sede.objects.all().delete()
    print("  - Importazione dal database, geolocalizzazione " + stringa("attiva" if args.geo else "disattiva"))
    n = carica_comitati(args.geo)
    print("  = Importati " + stringa(n) + " comitati.")
    print("  ~ Persisto tabella delle corrispondenze (comitati.pickle-tmp)")
    pickle.dump(ASSOC_ID_COMITATI, open("comitati.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (comitati.pickle-tmp)")
    ASSOC_ID_COMITATI = pickle.load(open("comitati.pickle-tmp", "rb"))

# Importazione delle Anagrafiche

print("> Importazione delle Anagrafiche")
if args.anagrafiche:
    print("  - Eliminazione attuali")
    Persona.objects.all().delete()
    Utenza.objects.all().delete()
    print("  - Importazione dal database")
    carica_anagrafiche()
    print("  ~ Persisto tabella delle corrispondenze (persone.pickle-tmp)")
    pickle.dump(ASSOC_ID_PERSONE, open("persone.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (persone.pickle-tmp)")
    ASSOC_ID_PERSONE = pickle.load(open("persone.pickle-tmp", "rb"))


# Importazione delle Appartenenze
print("> Importazione delle Appartenenze")
if args.appartenenze:
    print("  - Eliminazione attuali")
    Appartenenza.objects.all().delete()
    carica_appartenenze()
    print("  ~ Persisto tabella delle corrispondenze (appartenenze.pickle-tmp)")
    pickle.dump(ASSOC_ID_APPARTENENZE, open("appartenenze.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (appartenenze.pickle-tmp)")
    ASSOC_ID_APPARTENENZE = pickle.load(open("appartenenze.pickle-tmp", "rb"))


# Importazione delle Deleghe
print("> Importazione delle Deleghe")
if args.deleghe:
    print("  - Eliminazione attuali")
    Delega.objects.all().delete()
    carica_deleghe()
    print("  ~ Persisto tabella delle corrispondenze (deleghe.pickle-tmp)")
    pickle.dump(ASSOC_ID_DELEGHE, open("deleghe.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (deleghe.pickle-tmp)")
    ASSOC_ID_DELEGHE = pickle.load(open("deleghe.pickle-tmp", "rb"))


# Importazione delle Aree
print("> Importazione delle Aree")
if args.aree:
    print("  - Eliminazione attuali")
    Area.objects.all().delete()
    carica_aree()
    print("  ~ Persisto tabella delle corrispondenze (aree.pickle-tmp)")
    pickle.dump(ASSOC_ID_AREE, open("aree.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (aree.pickle-tmp)")
    ASSOC_ID_AREE = pickle.load(open("aree.pickle-tmp", "rb"))


# Importazione delle Attivita
print("> Importazione delle Attivita'")
if args.attivita:
    print("  - Eliminazione attuali")
    Attivita.objects.all().delete()
    carica_attivita()
    print("  ~ Persisto tabella delle corrispondenze (attivita.pickle-tmp)")
    pickle.dump(ASSOC_ID_ATTIVITA, open("attivita.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (attivita.pickle-tmp)")
    ASSOC_ID_ATTIVITA = pickle.load(open("attivita.pickle-tmp", "rb"))

# Importazione dei turni di attivita'
print("> Importazione dei Turni")
if args.turni:
    print("  - Eliminazione attuali")
    Turno.objects.all().delete()
    carica_turni()
    print("  ~ Persisto tabella delle corrispondenze (turni.pickle-tmp)")
    pickle.dump(ASSOC_ID_TURNI, open("turni.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (turni.pickle-tmp)")
    ASSOC_ID_TURNI = pickle.load(open("turni.pickle-tmp", "rb"))


# Importazione delle partecipazioni
print("> Importazione delle Partecipazioni (ed autorizzazioni)")
if args.partecipazioni:
    print("  - Eliminazione attuali")
    Partecipazione.objects.all().delete()
    carica_partecipazioni()
    print("  ~ Persisto tabella delle corrispondenze (partecipazioni.pickle-tmp)")
    pickle.dump(ASSOC_ID_PARTECIPAZIONI, open("partecipazioni.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (partecipazioni.pickle-tmp)")
    ASSOC_ID_PARTECIPAZIONI = pickle.load(open("partecipazioni.pickle-tmp", "rb"))


# Importazione delle quote
print("> Importazione delle Quote")
if args.quote:
    print("  - Eliminazione attuali")
    Tesseramento.objects.all().delete()
    Quota.objects.all().delete()

    carica_tesseramenti()
    carica_quote()

    print("  ~ Persisto tabella delle corrispondenze (tesseramenti.pickle-tmp)")
    pickle.dump(ASSOC_ID_TESSERAMENTI, open("tesseramenti.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (quote.pickle-tmp)")
    pickle.dump(ASSOC_ID_QUOTE, open("quote.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (tesseramenti.pickle-tmp)")
    ASSOC_ID_TESSERAMENTI = pickle.load(open("tesseramenti.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (quote.pickle-tmp)")
    ASSOC_ID_QUOTE = pickle.load(open("quote.pickle-tmp", "rb"))


# Importazione delle competenze e titoli
print("> Importazione dei Titoli")
if args.titoli:
    print("  - Eliminazione attuali")
    Titolo.objects.all().delete()
    TitoloPersonale.objects.all().delete()

    carica_titoli()
    carica_titoli_personali()

    print("  ~ Persisto tabella delle corrispondenze (titoli.pickle-tmp)")
    pickle.dump(ASSOC_ID_TITOLI, open("titoli.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (titolipersonali.pickle-tmp)")
    pickle.dump(ASSOC_ID_TITOLIPERSONALI, open("titolipersonali.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (titoli.pickle-tmp)")
    ASSOC_ID_TITOLI = pickle.load(open("titoli.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (titolipersonali.pickle-tmp)")
    ASSOC_ID_TITOLIPERSONALI = pickle.load(open("titolipersonali.pickle-tmp", "rb"))


# Importazione delle donazioni sangue
print("> Importazione delle Donazioni Sangue")
if args.sangue:
    print("  - Eliminazione attuali")

    sangue.Sede.objects.all().delete()
    sangue.Donatore.objects.all().delete()
    sangue.Merito.objects.all().delete()
    sangue.Donazione.objects.all().delete()

    carica_sangue_sedi()
    carica_sangue_donatori()
    carica_sangue_meriti()
    carica_sangue_donazioni()

    print("  ~ Persisto tabella delle corrispondenze (sangue-sedi.pickle-tmp)")
    pickle.dump(ASSOC_ID_SANGUE_SEDI, open("sangue-sedi.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (sangue-donatori.pickle-tmp)")
    pickle.dump(ASSOC_ID_SANGUE_DONATORI, open("sangue-donatori.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (sangue-meriti.pickle-tmp)")
    pickle.dump(ASSOC_ID_SANGUE_MERITI, open("sangue-meriti.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (sangue-donazioni.pickle-tmp)")
    pickle.dump(ASSOC_ID_SANGUE_DONAZIONI, open("sangue-donazioni.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (sangue-sedi.pickle-tmp)")
    ASSOC_ID_SANGUE_SEDI = pickle.load(open("sangue-sedi.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (sangue-donatori.pickle-tmp)")
    ASSOC_ID_SANGUE_DONATORI = pickle.load(open("sangue-donatori.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (sangue-meriti.pickle-tmp)")
    ASSOC_ID_SANGUE_MERITI = pickle.load(open("sangue-meriti.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (sangue-donazioni.pickle-tmp)")
    ASSOC_ID_SANGUE_DONAZIONI = pickle.load(open("sangue-donazioni.pickle-tmp", "rb"))


# Importazione dei commenti alle attivita
print("> Importazione dei commenti alle attivita")
if args.commenti:
    print("  - Eliminazione attuali")

    Commento.objects.all().delete()

    carica_commenti()

    print("  ~ Persisto tabella delle corrispondenze (commenti.pickle-tmp)")
    pickle.dump(ASSOC_ID_COMMENTI, open("commenti.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (commenti.pickle-tmp)")
    ASSOC_ID_COMMENTI = pickle.load(open("commenti.pickle-tmp", "rb"))


# Importazione dei corsi base e relativi
print("> Importazione dei corsi base")
if args.corsibase:
    print("  - Eliminazione attuali")

    formazione.CorsoBase.objects.all().delete()
    formazione.PartecipazioneCorsoBase.objects.all().delete()
    formazione.LezioneCorsoBase.objects.all().delete()
    formazione.AssenzaCorsoBase.objects.all().delete()

    carica_corsibase()
    carica_corsibase_lezioni()

    print("  ~ Persisto tabella delle corrispondenze (formazione-corsibase.pickle-tmp)")
    pickle.dump(ASSOC_ID_CORSIBASE, open("formazione-corsibase.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (formazione-corsibase-lezioni.pickle-tmp)")
    pickle.dump(ASSOC_ID_CORSIBASE_LEZIONI, open("formazione-corsibase-lezioni.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (formazione-corsibase-assenze.pickle-tmp)")
    pickle.dump(ASSOC_ID_CORSIBASE_ASSENZE, open("formazione-corsibase-assenze.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (formazione-corsibase-partecipazioni.pickle-tmp)")
    pickle.dump(ASSOC_ID_CORSIBASE_PARTECIPAZIONI, open("formazione-corsibase-partecipazioni.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (formazione-corsibase.pickle-tmp)")
    ASSOC_ID_CORSIBASE = pickle.load(open("formazione-corsibase.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (formazione-corsibase-lezioni.pickle-tmp)")
    ASSOC_ID_CORSIBASE_LEZIONI = pickle.load(open("formazione-corsibase-lezioni.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (formazione-corsibase-assenze.pickle-tmp)")
    ASSOC_ID_CORSIBASE_ASSENZE = pickle.load(open("formazione-corsibase-assenze.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (formazione-corsibase-partecipazioni.pickle-tmp)")
    ASSOC_ID_CORSIBASE_PARTECIPAZIONI = pickle.load(open("formazione-corsibase-partecipazioni.pickle-tmp", "rb"))



# Importazione degli aspiranti
print("> Importazione degli aspiranti")
if args.aspiranti:
    print("  - Eliminazione attuali")

    formazione.Aspirante.objects.all().delete()

    carica_aspiranti()

    print("  ~ Persisto tabella delle corrispondenze (formazione-aspiranti.pickle-tmp)")
    pickle.dump(ASSOC_ID_ASPIRANTI, open("formazione-aspiranti.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (formazione-aspiranti.pickle-tmp)")
    ASSOC_ID_ASPIRANTI = pickle.load(open("formazione-aspiranti.pickle-tmp", "rb"))


# Importazione dei trasferimenti
print("> Importazione dei trasferimetni")
if args.trasferimenti:
    print("  - Eliminazione attuali")

    Trasferimento.objects.all().delete()
    carica_trasferimenti()

    print("  ~ Persisto tabella delle corrispondenze (trasferimenti.pickle-tmp)")
    pickle.dump(ASSOC_ID_TRASFERIMENTI, open("trasferimenti.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (formazione-aspiranti.pickle-tmp)")
    ASSOC_ID_TRASFERIMENTI = pickle.load(open("trasferimenti.pickle-tmp", "rb"))

# print(ASSOC_ID_COMITATI)