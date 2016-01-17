# -*- coding: utf-8 -*-

import os, sys

from django.utils.encoding import smart_str
os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

import phonenumbers
from django.core.files import File

from anagrafica.validators import ottieni_genere_da_codice_fiscale
from base.notifiche import NOTIFICA_NON_INVIARE
from base.stringhe import GeneratoreNomeFile
from base.utils import poco_fa


from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
from anagrafica.permessi.applicazioni import PRESIDENTE, DELEGATO_AREA, REFERENTE, DELEGATO_OBIETTIVO_1, \
    DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, \
    DELEGATO_CO, UFFICIO_SOCI, RESPONSABILE_PATENTI, RESPONSABILE_FORMAZIONE, UFFICIO_SOCI_TEMPORANEO, \
    RESPONSABILE_AUTOPARCO, RESPONSABILE_DONAZIONI, DIRETTORE_CORSO, REFERENTE_GRUPPO
from attivita.models import Area, Attivita, Partecipazione, Turno
from base.models import Autorizzazione
from curriculum.models import TitoloPersonale, Titolo
from social.models import Commento

from veicoli.models import Autoparco, FermoTecnico
from veicoli.models import Collocazione
from veicoli.models import Manutenzione
from veicoli.models import Rifornimento
from veicoli.models import Veicolo

import pickle
import sangue.models as sangue
from django.contrib.gis.geos import Point
from autenticazione.models import Utenza
import formazione.models as formazione
import gruppi.models as gruppi
from formazione.models import PartecipazioneCorsoBase

from safedelete import HARD_DELETE
from jorvik.settings import MYSQL_CONF

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.template.backends import django
from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from anagrafica.models import Sede, Persona, Appartenenza, Delega, Trasferimento, Fototessera, Documento, Estensione, \
    ProvvedimentoDisciplinare, Dimissione
from base.geo import Locazione
from ufficio_soci.models import Quota, Tesseramento, Tesserino
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
    #    #return smart_str(s.encode('utf-8'))
    #except:
    return ftfy.fix_text(smart_str(s), fix_entities=False)

parser = argparse.ArgumentParser(description='Importa i dati da un database MySQL di PHP-Gaia.')
parser.add_argument('--no-geo', dest='geo', action='store_const',
                   const=False, default=True,
                   help='disattiva le funzionalita geografiche (solo test)')
parser.add_argument('-v', dest='verbose', action='store_const',
                   const=True, default=False,
                   help='mostra dettagli sul progresso (estremamente prolisso)')
parser.add_argument('--salta-comitati', dest='comitati', action='store_const',
                   const=False, default=True,
                   help='salta importazione comitati (usa cache precedente)')
parser.add_argument('--salta-anagrafiche', dest='anagrafiche', action='store_const',
                   const=False, default=True,
                   help='salta importazione anagrafiche (usa cache precedente)')
parser.add_argument('--salta-avatar', dest='avatar', action='store_const',
                   const=False, default=True,
                   help='salta importazione avatar')
parser.add_argument('--salta-fototessere', dest='fototessere', action='store_const',
                   const=False, default=True,
                   help='salta importazione fototessere')
parser.add_argument('--salta-documenti', dest='documenti', action='store_const',
                   const=False, default=True,
                   help='salta importazione documenti')
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
parser.add_argument('--salta-estensioni', dest='estensioni', action='store_const',
                   const=False, default=True,
                   help='salta importazione estensioni (usa cache precedente)')
parser.add_argument('--salta-veicoli', dest='veicoli', action='store_const',
                   const=False, default=True,
                   help='salta importazione autoparco, veicoli e correlati (usa cache precedente)')
parser.add_argument('--salta-tesserini', dest='tesserini', action='store_const',
                   const=False, default=True,
                   help='salta importazione richieste di tesserino (usa cache precedente)')
parser.add_argument('--salta-gruppi', dest='gruppi', action='store_const',
                   const=False, default=True,
                   help='salta importazione gruppi')
parser.add_argument('--salta-dipendenti', dest='dipendenti', action='store_const',
                   const=False, default=True,
                   help='salta importazione dipendenti')
parser.add_argument('--salta-provvedimenti', dest='provvedimenti', action='store_const',
                   const=False, default=True,
                   help='salta importazione provvedimenti disciplinari')
parser.add_argument('--salta-dimissioni', dest='dimissioni', action='store_const',
                   const=False, default=True,
                   help='salta importazione dimissioni')
parser.add_argument('--salta-privacy', dest='privacy', action='store_const',
                   const=False, default=True,
                   help='salta importazione privacy')

parser.add_argument('--uploads', dest='uploads', action='store',
                   help='path assoluta alla cartella upload/ di Gaia vecchio')

parser.add_argument('--ignora-errori-db', dest='ignora', action='store_const',
                   const=True, default=False,
                   help='ignora errori di integrita (solo test)')


args = parser.parse_args()

def ffloat(n, default=0.0):
    try:
        return float(n)
    except ValueError:
        return float(default)

def iint(n, default=0):
    try:
        return int(n)
    except ValueError:
        return iint(default)
    except TypeError:
        return iint(default)

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

ASSOC_ID_ESTENSIONI = {}

ASSOC_ID_AUTOPARCHI = {}
ASSOC_ID_VEICOLI = {}
ASSOC_ID_TESSERINI = {}
ASSOC_ID_GRUPPI = {}


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
            id, nome, X(geo), Y(geo)""" + (", principale, attivo" if tipo == 'comitati' else " ") + """
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
        'principale': (True if comitato[4] else False) if len(comitato) > 4 else False,
        'attivo': (True if int(comitato[5]) == 1 else False) if len(comitato) > 5 else True,
        'dati': dict
    }

def path(filename):
    if not args.uploads:
        raise ValueError("Path non specificata. Usare --uploads.")
    return args.uploads + (smart_str(filename))

def esiste(filename):
    return os.path.isfile(filename)

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
    timestamp = iint(timestamp)
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

    totale = cursore.rowcount
    contatore = 0
    for persona in persone:

        contatore += 1

        if args.verbose:
            print("    - " + progresso(contatore, totale) + ": id=" + stringa(persona[0]) + ", codice_fiscale=" + stringa(persona[6]))

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
        genere_registrato = Persona.MASCHIO if dati['sesso'] == 1 else Persona.FEMMINA
        genere = ottieni_genere_da_codice_fiscale(dati['codiceFiscale'], default=genere_registrato)
        codice_fiscale = dati['codiceFiscale']
        p = Persona(
            nome=dati['nome'],
            cognome=dati['cognome'],
            codice_fiscale=codice_fiscale,
            data_nascita=data_nascita,
            genere=genere,
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

        vecchia_sede = None

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
            vecchia_sede = comitato
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

        creazione = data_da_timestamp(app[4], default=inizio)
        ultima_modifica = creazione

        # Creazione della nuova appartenenza
        a = Appartenenza(
            persona=persona,
            sede=comitato,
            inizio=inizio,
            fine=fine,
            confermata=confermata,
            membro=membro,
            terminazione=terminazione,
            vecchia_sede=vecchia_sede,
            creazione=creazione,
            ultima_modifica=ultima_modifica,
        )
        a.save()

        # Pendenti.
        if stato == 30:  # MEMBRO_PENDENTE
            if args.verbose:
                print("      - Pendente, richiesta autorizzazione")

            a.autorizzazione_richiedi(
                persona,
                ((PRESIDENTE, comitato.comitato),),
                creazione=creazione,
                ultima_modifica=ultima_modifica,
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

    if comitato['principale']:
        ASSOC_ID_COMITATI[COMITATO_OID[tipo]].update({id: (Sede, ref.pk)})
        c = ref

    # Sedi principali (locali con nome Provinciale diventano Provinciale)
    elif ref and COMITATO_ESTENSIONE[tipo] == LOCALE \
            and stringa(comitato['nome']) == ref.nome:
        ASSOC_ID_COMITATI[COMITATO_OID[tipo]].update({id: (Sede, ref.pk)})
        c = ref

    else:

        attiva = True
        if not comitato['attivo']:
            attiva = False

        c = Sede(
            genitore=ref,
            nome=stringa(comitato['nome']),
            tipo=Sede.COMITATO,
            estensione=COMITATO_ESTENSIONE[tipo],
            vecchio_id=int(id),
            attiva=attiva,
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
        print("    - %s [%d] %s: %s" % ("-" * num, comitato['principale'], c.nome, stringa(c.locazione)))

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
                  (id, smart_str(sede.pk) if sede else None, persona.codice_fiscale if persona else None))


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

        try:
            registrato_da = ASSOC_ID_PERSONE[int(quota[6])]
        except KeyError:
            print("    - Quota Saltata (%d) registrato da persona non esistente (%d)" % (
                id, int(quota[6]),
            ))
            continue

        importo = float(quota[7])

        causale = stringa(quota[8]) or ''
        causale_extra = stringa(quota[9]) or ''
        anno = int(quota[10])

        annullato_da = ASSOC_ID_PERSONE[int(quota[11])] if quota[11] else None
        data_annullamento = data_da_timestamp(quota[12], data_creazione)

        stato = Quota.REGISTRATA if annullato_da is None else Quota.ANNULLATA

        progressivo = int(quota[13])

        importo_extra = 0.0

        causale_lowercase = causale.lower()
        if "iscrizione" in causale_lowercase or "ordinar" in causale_lowercase:
            if importo > 16.0:
                importo_extra = importo - 16.00
                importo = 16.0

        elif "attivo" in causale_lowercase:
            if importo > 8.0:
                importo_extra = importo - 8.0
                importo = 8.0

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
                creazione=data_versamento,
                ultima_modifica=data_annullamento if data_annullamento else data_versamento,
                vecchio_id=id,
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

        try:
            pConferma = ASSOC_ID_PERSONE[int(titolo[9])] if titolo[9] else None

        except KeyError:
            print("    - SALTATO pConferma non trovata %d " % (int(titolo[9]),))
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
            progresso(contatore, totale), smart_str(s),
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
            progresso(contatore, totale), smart_str(d),
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
            vecchio_id=id,
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
            lezioni_assenze
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
            registrata_da_id=registrato_da_id,
            creazione=tConferma,
            ultima_modifica=tConferma,
        )
        a.save()

        ASSOC_ID_CORSIBASE_ASSENZE[id] = a.pk

    cursore.close()


def carica_corsibase_partecipazioni():

    print("  - Caricamento delle partecipazioni lezioni ai corsi base...")

    print("    - Caricamento dettagli in memoria...")
    dd = generatore_funzione_dettaglio('datiPartecipazioniBase')

    print("    - Caricamento partecipazioni...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, corsoBase,
            stato, timestamp, tConferma,
            pConferma, tAttestato, cAttestato
        FROM
            partecipazioniBase
        WHERE
            volontario IN (SELECT id FROM anagrafica)
        AND corsoBase IN (SELECT id FROM corsibase)
        """
    )

    pcbs = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for pcb in pcbs:
        contatore += 1

        id = int(pcb[0])

        try:
            persona_id = ASSOC_ID_PERSONE[int(pcb[1])]
        except KeyError:
            print("    SALTATO persona non esistente")
            continue

        try:
            pConferma_id = ASSOC_ID_PERSONE[int(pcb[6])] if pcb[6] else None
        except KeyError:
            print("    SALTATO persona pConferma non esistente")
            continue

        try:
            pAttestato_id = ASSOC_ID_PERSONE[int(pcb[8])] if pcb[8] else None
        except KeyError:
            print("    SALTATO persona cAttestato non esistente")
            continue

        try:
            corso_id = ASSOC_ID_CORSIBASE[int(pcb[2])]
        except KeyError:
            print("    SALTATO corso base non esistente")
            continue

        corso = formazione.CorsoBase.objects.get(pk=corso_id)

        stato = int(pcb[3])

        creazione = data_da_timestamp(pcb[4])

        tConferma = data_da_timestamp(pcb[5], default=None)
        tAttestato = data_da_timestamp(pcb[7], default=None)

        ammissione = None
        motivo_non_ammissione = ''
        esito = None
        esito_parte_1 = None
        esito_parte_2 = None
        argomento_parte_1 = None
        argomento_parte_2 = None

        ritirata = False
        confermata = True

        a = None

        if stato == 50:  # Bocciato

            esito = PartecipazioneCorsoBase.NON_IDONEO
            motivo_non_ammissione = stringa(dd(id, 'motivo')) or 'Non specificato'

            if motivo_non_ammissione == "non presente all'esame":
                ammissione = PartecipazioneCorsoBase.ASSENTE

            elif "non amesso per" in motivo_non_ammissione:
                ammissione = PartecipazioneCorsoBase.NON_AMMESSO

        elif stato == 40:  # Superato

            esito = PartecipazioneCorsoBase.IDONEO

            p = PartecipazioneCorsoBase.POSITIVO
            n = PartecipazioneCorsoBase.NEGATIVO

            extra_1 = bool(dd(id, 'e1', default=0))
            extra_2 = bool(dd(id, 'e2', default=0))

            esito_parte_1 = p
            argomento_parte_1 = stringa(dd(id, 'a1')) or ''

            if not extra_2:
                esito_parte_2 = p if iint(dd(id, 'p2')) else n
                argomento_parte_2 = stringa(dd(id, 'a2')) or ''


        elif stato == 30:  # Iscritto e confermato

            a = {
                "richiedente_id": persona_id,
                "firmatario_id": pConferma_id,
                "concessa": True,
                "necessaria": False,
                "progressivo": 1,
                "destinatario_ruolo": DIRETTORE_CORSO,
                "destinatario_oggetto": corso,
                "creazione": creazione,
                "ultima_modifica": tConferma,
            }

        elif stato == 20:  # Richiesto (preiscritto)

            confermata = False
            a = {
                "richiedente_id": persona_id,
                "firmatario_id": None,
                "concessa": None,
                "necessaria": True,
                "progressivo": 1,
                "destinatario_ruolo": DIRETTORE_CORSO,
                "destinatario_oggetto": corso,
                "creazione": creazione,
                "ultima_modifica": creazione,
            }


        elif stato == 10:  # Abbandono (non previsto)
            raise ValueError("Abbandono non previsto.")

        elif stato == 5:  # Negato
            confermata = False
            a = {
                "richiedente_id": persona_id,
                "firmatario_id": pConferma_id,
                "concessa": False,
                "necessaria": False,
                "progressivo": 1,
                "destinatario_ruolo": DIRETTORE_CORSO,
                "destinatario_oggetto": corso,
                "creazione": creazione,
                "ultima_modifica": tConferma,
            }

        elif stato == 0:  # Ritirata
            confermata = False
            ritirata = True
            a = {
                "richiedente_id": persona_id,
                "firmatario_id": None,
                "concessa": None,
                "necessaria": False,
                "progressivo": 1,
                "destinatario_ruolo": DIRETTORE_CORSO,
                "destinatario_oggetto": corso,
                "creazione": creazione,
                "ultima_modifica": creazione,
            }

        p = PartecipazioneCorsoBase(
            persona_id=persona_id,
            corso=corso,
            esito_esame=esito,
            ammissione=ammissione,
            motivo_non_ammissione=motivo_non_ammissione,
            esito_parte_1=esito_parte_1,
            argomento_parte_1=argomento_parte_1,
            esito_parte_2=esito_parte_2,
            argomento_parte_2=argomento_parte_2,
            extra_1=extra_1,
            extra_2=extra_2,
            creazione=creazione,
            ultima_modifica=tAttestato if tAttestato else (tConferma if tConferma else creazione),
            confermata=confermata,
            ritirata=ritirata,
        )
        p.save()

        if a:
            au = Autorizzazione(oggetto=p, **a)
            au.save()

        print("   %s partecipazione corsobase id=%d, persona id=%d, aut=%d" % (
            progresso(contatore, totale), corso_id, persona_id, bool(a),
        ))

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


def carica_avatar():

    print("  - Caricamento degli avatar...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, utente, timestamp
        FROM
            avatar
        WHERE
                utente IS NOT NULL
        """
    )

    avatars = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    generatore = GeneratoreNomeFile('avatar/')

    for avatar in avatars:
        contatore += 1

        try:
            id = int(avatar[0])
            utente = int(avatar[1])

        except ValueError:
            print("    - SALTATO Record non valido.")
            continue

        try:
            persona = Persona.objects.get(pk=ASSOC_ID_PERSONE[utente])
        except KeyError:
            print("    - SALTATO Persona id=%d non esiste" % (utente,))
            continue

        nomefile = path("avatar/80/%d.jpg" % (id,))
        try:
            originale = open(nomefile, 'rb')
        except:
            print("    - SALTATO File non esiste path=%s" % (nomefile,))
            continue

        dfile = File(originale)
        nuovonome = generatore(persona, nomefile)
        persona.avatar.save(nuovonome, dfile, save=True)
        print("     %s OK persona id=%d, avatar=%s" % (progresso(contatore, totale), utente, nuovonome,))


    cursore.close()


def carica_fototessere():

    print("  - Caricamento delle fototessere...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, utente, timestamp, stato
        FROM
            fototessera
        WHERE
                utente IS NOT NULL
        AND     utente IN (SELECT id FROM anagrafica)

        """
    )

    fts = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    generatore = GeneratoreNomeFile('fototessere/')

    for ft in fts:
        contatore += 1

        try:
            id = int(ft[0])
            utente = int(ft[1])

        except ValueError:
            print("    - SALTATO Record non valido.")
            continue

        creazione = data_da_timestamp(ft[2])
        stato = int(ft[3])

        try:
            persona = Persona.objects.get(pk=ASSOC_ID_PERSONE[utente])
        except KeyError:
            print("    - SALTATO Persona id=%d non esiste" % (utente,))
            continue

        nomefile = path("fototessere/80/%d.jpg" % (id,))
        try:
            originale = open(nomefile, 'rb')
        except:
            print("    - SALTATO File non esiste path=%s" % (nomefile,))
            continue

        dfile = File(originale)
        nuovonome = generatore(persona, nomefile)

        print("     %s persona id=%d, fototessera=%s" % (progresso(contatore, totale), utente, nuovonome,))

        f = Fototessera(
            persona=persona,
            creazione=creazione,
            ultima_modifica=creazione,
        )
        f.save()
        f.file.save(nuovonome, dfile, save=True)

        if stato == 0:  # Se pending.
            s = persona.comitato_riferimento()
            if not s:
                print("    - SALTATO pending, ma non ha appartenenza attuale.")
                f.delete()
                continue
            print("    - richiesta autorizzazione a presidente e us sede pk=%d" % (s.pk,))
            f.autorizzazione_richiedi(richiedente=persona,
                                      destinatario=(
                                          (PRESIDENTE,  s,  NOTIFICA_NON_INVIARE),
                                          (UFFICIO_SOCI, s, NOTIFICA_NON_INVIARE)
                                      ),
                                      creazione=creazione)


    cursore.close()


def carica_documenti():

    print("  - Caricamento dei documenti...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, tipo, timestamp
        FROM
            documenti
        WHERE
                volontario IS NOT NULL
            AND id IS NOT NULL
        """
    )

    docs = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    generatore = GeneratoreNomeFile('documenti/')

    for doc in docs:
        contatore += 1

        try:
            id = stringa(doc[0])
            utente = int(doc[1])

        except ValueError:
            print("    - SALTATO Record non valido.")
            continue

        tipo = int(doc[2])
        timestamp = data_da_timestamp(doc[3])

        try:
            persona_id = ASSOC_ID_PERSONE[utente]
        except KeyError:
            print("    - SALTATO Persona id=%d non esiste" % (utente,))
            continue

        nomefile = path("docs/o/%s.jpg" % (id,))
        try:
            originale = open(nomefile, 'rb')
        except:
            print("    - SALTATO File non esiste path=%s" % (nomefile,))
            continue

        if tipo == 10:
            tipo = Documento.CARTA_IDENTITA
        elif tipo == 20:
            tipo = Documento.PATENTE_CIVILE
        elif tipo == 40:
            tipo = Documento.CODICE_FISCALE
        elif tipo == 50:
            tipo = Documento.PATENTE_CRI
        else:
            tipo = Documento.ALTRO

        dfile = File(originale)

        d = Documento(
            tipo=tipo,
            persona_id=persona_id,
        )
        d.save()

        nuovonome = generatore(d, nomefile)
        d.file.save(nuovonome, dfile, save=True)
        print("     %s OK persona id=%d, documento=%s" % (progresso(contatore, totale), utente, nuovonome,))


    cursore.close()

@transaction.atomic
def carica_estensioni():

    print("  - Caricamento delle estensioni...")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, stato, appartenenza, volontario, cProvenienza, protNumero, protData,
            motivo, negazione, timestamp, pConferma, tConferma
        FROM
            estensioni
        WHERE
            volontario IN (SELECT id FROM anagrafica)
        AND appartenenza IN (SELECT id FROM appartenenza)
        AND cProvenienza IN (SELECT id FROM comitati)
        """
    )

    ests = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for est in ests:
        contatore += 1

        id = int(est[0])
        stato = int(est[1])
        appartenenza_id = int(est[2])
        persona_id = int(est[3])
        # sede_provenienza = int(est[4])  # Non importa davvero piu.
        protocollo_numero = stringa(est[5])
        protocollo_data = data_da_timestamp(est[6], None) if est[6] else None
        motivo = stringa(est[7])
        negazione = stringa(est[8])
        creazione = data_da_timestamp(est[9])
        pConferma_id = int(est[10]) if est[10] else None
        tConferma = data_da_timestamp(est[11], None) if est[11] else None

        print("    %s estensione id=%d, persona=%d, appartenenza=%d" % (
            progresso(contatore, totale),
            id, persona_id, appartenenza_id,
        ))

        try:
            appartenenza_id = ASSOC_ID_APPARTENENZE[appartenenza_id]
            appartenenza = Appartenenza.objects.get(pk=appartenenza_id)

        except KeyError:
            print("     - SALTATO appartenenza id=%d non trovata " % (appartenenza_id, ))
            continue

        try:
            persona_id = ASSOC_ID_PERSONE[persona_id]
            persona = Persona.objects.get(pk=persona_id)

        except KeyError:
            print("     - SALTATO persona id=%d non trovata " % (persona_id,))
            continue

        approvata = False
        if stato == 40 or (pConferma_id is not None and not negazione):  # Se approvata
            approvata = True

        ultima_modifica = creazione if tConferma is None else max(creazione, tConferma)

        confermata = True if approvata and stato != 10 and stato != 25 else False
        ritirata = True if stato == 25 else False

        sede_riferimento = persona.comitato_riferimento(al_giorno=creazione)
        if not sede_riferimento and stato == 20:
            print("      - SALTATO Nessuna sede di riferimento al momento della creazione")
            continue

        e = Estensione(
            richiedente_id=persona_id,
            persona_id=persona_id,
            destinazione=appartenenza.sede,
            appartenenza=appartenenza if approvata else None,  # Collega appartenenza solo se approvata.
            protocollo_numero=protocollo_numero or '',
            protocollo_data=protocollo_data or None,
            motivo=motivo if motivo else '',
            creazione=creazione,
            ultima_modifica=ultima_modifica,
            confermata=confermata,
            ritirata=ritirata,
        )
        e.save()

        if stato == 20:  # In corso
            firmatario_id = None
            necessaria = True
            concessa = None

        elif stato == 10:
            firmatario_id = pConferma_id
            necessaria = False
            concessa = False

        elif stato == 25:
            firmatario_id = None
            necessaria = False
            concessa = None

        elif stato == 0 or stato == 30:
            firmatario_id = pConferma_id
            necessaria = False
            concessa = True

        if sede_riferimento and not stato == 40:  # Approvata automaticamente, nessuna autorizzazione.

            print("     - Creo autorizzazione associata a presidente sede pk=%d" % (sede_riferimento.pk,))

            a = Autorizzazione(
                oggetto=e,
                richiedente_id=persona_id,
                firmatario_id=firmatario_id,
                concessa=concessa,
                motivo_negazione=negazione,
                necessaria=necessaria,
                destinatario_ruolo=PRESIDENTE,
                destinatario_oggetto=sede_riferimento,
            )
            a.save()

    cursore.close()


def carica_autoparchi():

    print("  - Caricamento degli autoparchi...")

    dett = generatore_funzione_dettaglio('dettagliAutoparco')
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            a.id, a.nome, a.comitato
        FROM
            autoparchi AS a
        """
    )

    auts = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0


    for aut in auts:
        contatore += 1

        id = int(aut[0])
        nome = stringa(aut[1])
        comitato = comitato_oid(aut[2])

        posizione = dett(id, 'formattato', default=None)
        tel = dett(id, 'telefono', default='')

        print("   %s Autoparco id=%d, nome=%s, comitato id=%d" % (
            progresso(contatore, totale), id, nome, comitato.pk,
        ))
        a = Autoparco(
            nome=nome,
            sede=comitato,
            estensione=comitato.estensione,
            telefono=tel,
        )
        a.save()

        ASSOC_ID_AUTOPARCHI[id] = a.pk

        if posizione and args.geo:
            a.imposta_locazione(posizione)
            print("     - Posizione: %s" % (posizione,))


    cursore.close()


def ottieni_dettaglio(tabella, id, nome, default=None):
    c = db.cursor()
    c.execute("SELECT valore FROM %s WHERE id=%d AND nome='%s'" % (tabella, id, nome,))
    ca = c.fetchall()
    if not ca:
        va = default
    else:
        va = ca[0][0]
        if va is None or va == "":
            va = default
    c.close()
    return va


def generatore_funzione_dettaglio(tabella):
    DE = {}

    print("  - Caricamento dettagli (%s)... " % (tabella,))

    ak = db.cursor()
    ak.execute("SELECT id, nome, valore FROM %s" % (tabella,))
    aks = ak.fetchall()
    for d in aks:
        try:
            DE["%d:%s" % (int(d[0]), d[1],)] = d[2]
        except ValueError:
            pass
    ak.close()
    def _dve(id, nome, default=None):
        try:
            v = DE["%d:%s" % (int(id), nome)]
        except KeyError:
            v = default
        except ValueError:
            v = default
        if not v or v == "":
            v = default
        return v
    return _dve



def carica_veicoli():

    dve = generatore_funzione_dettaglio('dettagliVeicolo')

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, targa, libretto, telaio, comitato, stato, pFuoriuso, tFuoriuso
        FROM veicoli
        WHERE targa IS NOT NULL
                AND targa <> ''
                AND comitato IS NOT NULL

        """
    )

    ves = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    TELAIO = {}

    for ve in ves:
        contatore += 1

        id = int(ve[0])
        targa = stringa(ve[1])
        libretto = stringa(ve[2])
        telaio = stringa(ve[3])

        if telaio:
            while telaio in TELAIO:
                telaio = "%s-bis" % (telaio,)
            TELAIO[telaio] = True

        comitato = stringa(ve[4])
        stato = iint(ve[5]) if ve[5] else None
        if stato == 20:
            stato = Veicolo.DISMESSO
        else:
            stato = Veicolo.IN_SERVIZIO
        tFuoriuso = data_da_timestamp(ve[7])

        prima_immatricolazione = data_da_timestamp(dve(id, 'primaImmatricolazione', None))
        cognome = stringa(dve(id, 'cognome', default='N/D'))
        nome = stringa(dve(id, 'nome', default='N/D'))
        indirizzo = stringa(dve(id, 'indirizzo', default='N/D'))
        anteriori = stringa(dve(id, 'anteriori', default='N/D'))
        posteriori = stringa(dve(id, 'posteriori', default='N/D'))
        altAnt = stringa(dve(id, 'altAnt', default='N/D'))
        altPost = stringa(dve(id, 'altPost', default='N/D'))
        cambio = stringa(dve(id, 'cambio', default='N/D'))
        lunghezza = ffloat(dve(id, 'lunghezza', default=0.0))
        larghezza = ffloat(dve(id, 'larghezza', default=0.0))
        sbalzo = ffloat(dve(id, 'sbalzo', default=0.0))
        tara = iint(dve(id, 'tara', default=0))

        marca = stringa(dve(id, 'marca', default='N/D'))
        modello = stringa(dve(id, 'tipo', default='N/D'))
        massa = iint(dve(id, 'massa', default=1))
        immatricolazione = data_da_timestamp(dve(id, 'immatricolazione', None))

        categoria = stringa(dve(id, 'categoria', default='N/D'))
        uso = stringa(dve(id, 'uso', default='N/D'))
        carrozzeria = stringa(dve(id, 'carrozzeria', default='N/D'))
        omologazione = stringa(dve(id, 'omologazione', default='N/D'))
        assi = iint(dve(id, 'assi', default=2))
        rimorchio_frenato = ffloat(dve(id, 'rimorchioFrenato', default=0.0))

        cilindrata = iint(dve(id, 'cilindrata', default=2))
        potenza = iint(dve(id, 'potenza', default=2))

        alimentazione = stringa(dve(id, 'alimentazione', default='N/D'))
        if alimentazione == 'BENZINA':
            alimentazione = Veicolo.BENZINA
        elif alimentazione == 'GASOLIO':
            alimentazione = Veicolo.GASOLIO
        else:
            alimentazione = None

        posti = iint(dve(id, 'posti', default=2))
        regime = iint(dve(id, 'regime', default=2))

        creazione = data_da_timestamp(dve(id, 'tInserimento'))

        intervallo_revisione = iint(dve(id, 'intervalloRevisione', default=31556926))
        if intervallo_revisione == 63113852:
            intervallo_revisione = 730
        else:
            intervallo_revisione = 365

        print("   %s veicolo id=%d, targa=%s" % (
            progresso(contatore, totale), id, targa
        ))

        v = Veicolo(
            stato=stato,
            libretto=libretto,
            targa=targa,
            prima_immatricolazione=prima_immatricolazione,
            proprietario_nome=nome,
            proprietario_cognome=cognome,
            proprietario_indirizzo=indirizzo,
            pneumatici_anteriori=anteriori,
            pneumatici_posteriori=posteriori,
            pneumatici_alt_anteriori=altAnt,
            pneumatici_alt_posteriori=altPost,
            cambio=cambio,
            lunghezza=lunghezza,
            larghezza=larghezza,
            sbalzo=sbalzo,
            tara=tara,
            marca=marca,
            modello=modello,
            telaio=telaio,
            massa_max=massa,
            data_immatricolazione=immatricolazione,
            categoria=categoria,
            destinazione=uso,
            carrozzeria=carrozzeria,
            omologazione=omologazione,
            num_assi=assi,
            rimorchio_frenato=rimorchio_frenato,
            cilindrata=cilindrata,
            potenza_massima=potenza,
            alimentazione=alimentazione,
            posti=posti,
            regime=regime,
            intervallo_revisione=intervallo_revisione,
            creazione=creazione or None,
            ultima_modifica=creazione or None,
        )
        v.save()

        ASSOC_ID_VEICOLI[id] = v.pk
    cursore.close()


def carica_collocazioni():


    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, veicolo, autoparco, pConferma, tConferma, inizio, fine, pFine, tFine
        FROM collocazioneVeicoli

        """
    )

    cos = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0


    for co in cos:
        contatore += 1

        id = int(co[0])
        try:
            veicolo = ASSOC_ID_VEICOLI[iint(co[1])]
        except KeyError:
            print("   SALTATO veicolo non esistente ")
            continue
        try:
            autoparco = ASSOC_ID_AUTOPARCHI[iint(co[2])]
        except KeyError:
            print("   SALTATO autoparco non esistente ")
            continue
        try:
            pConferma = ASSOC_ID_PERSONE[iint(co[3])]
        except KeyError:
            print("   SALTATO persona non esistente ")
            continue

        tConferma = data_da_timestamp(co[4])
        inizio = data_da_timestamp(co[5])
        fine = data_da_timestamp(co[6], default=None)

        print("   %s collocazione id=%d, veicolo=%d, autoparco=%d" % (
            progresso(contatore, totale), id, veicolo, autoparco,
        ))

        c = Collocazione(
            veicolo_id=veicolo,
            autoparco_id=autoparco,
            creazione=tConferma,
            ultima_modifica=tConferma,
            creato_da_id=pConferma,
            inizio=inizio,
            fine=fine,
        )
        c.save()
    cursore.close()


def carica_manutenzioni():


    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, veicolo, intervento,
            tIntervento, tRegistra, pRegistra, km,
            tipo, costo, fattura, azienda
        FROM
            manutenzioni
        WHERE
            tIntervento IS NOT NULL
        AND tRegistra IS NOT NULL
        AND veicolo IN (SELECT id FROM veicoli)

        """
    )

    mans = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0


    for man in mans:
        contatore += 1

        id = int(man[0])
        try:
            veicolo = ASSOC_ID_VEICOLI[iint(man[1])]
        except KeyError:
            print("   SALTATO veicolo non esistente ")
            continue

        try:
            persona_id = ASSOC_ID_PERSONE[iint(man[5])]
        except KeyError:
            print("   SALTATO persona non esistente ")
            continue

        descrizione = stringa(man[2]) or 'N/D'
        data = data_da_timestamp(man[3])
        creazione = data_da_timestamp(man[4], data)
        km = ffloat(man[6], default=0.0)
        tipo = iint(man[7])
        if tipo == 10:
            tipo = Manutenzione.MANUTENZIONE_ORDINARIA
        elif tipo == 30:
            tipo = Manutenzione.REVISIONE
        else:
            tipo = Manutenzione.MANUTENZIONE_STRAORDINARIA

        creato_da_id = persona_id
        costo = ffloat(man[8], default=0.0)
        if costo < 0:
            costo = 0
        numero_fattura = stringa(man[9])
        manutentore = stringa(man[10])

        print("   %s manutenzione id=%d, veicolo=%d, tipo=%s" % (
            progresso(contatore,totale),
            id, veicolo, tipo
        ))

        m = Manutenzione(
            veicolo_id=veicolo,
            tipo=tipo,
            data=data,
            descrizione=descrizione,
            km=km,
            manutentore=manutentore,
            numero_fattura=numero_fattura,
            costo=costo,
            creato_da_id=creato_da_id
        )
        m.save()

    cursore.close()


def carica_rifornimenti():

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, pRegistra, tRegistra,
            km, data, veicolo,
            timestamp, litri, costo
        FROM
            rifornimento
        WHERE
            pRegistra IN (SELECT id FROM anagrafica)
        AND veicolo IN (SELECT id FROM veicoli)
        """
    )

    rifs = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for rif in rifs:
        contatore += 1

        id = int(rif[0])

        try:
            persona_id = ASSOC_ID_PERSONE[iint(rif[1])]
        except KeyError:
            print("   SALTATO veicolo non esistente ")
            continue

        try:
            veicolo_id = ASSOC_ID_VEICOLI[iint(rif[5])]
        except KeyError:
            print("   SALTATO veicolo non esistente ")
            continue

        tRegistra = data_da_timestamp(rif[2])

        km = iint(rif[3], default=0)
        data = data_da_timestamp(rif[4])
        litri = ffloat(rif[7])
        costo = ffloat(rif[8])

        print("   %s rifornimento id=%d, veicolo=%d" % (
            progresso(contatore, totale),
            id, veicolo_id
        ))

        r = Rifornimento(
            veicolo_id=veicolo_id,
            data=data,
            contachilometri=km,
            costo=costo,
            consumo_carburante=litri,
            presso=None,
            contalitri=None,
            creazione=tRegistra,
            ultima_modifica=tRegistra
        )
        r.save()

    cursore.close()


def carica_fermi_tecnici():

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, veicolo, inizio,
            fine, motivo, pInizio,
            tInizio, pFine, tFine
        FROM
            fermotecnico
        WHERE
            veicolo IN (SELECT id FROM veicoli)
        AND pInizio IN (SELECT id FROM anagrafica)
        """
    )

    ferms = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for ferm in ferms:
        contatore += 1

        id = int(ferm[0])

        try:
            persona_id = ASSOC_ID_PERSONE[iint(ferm[5])]
        except KeyError:
            print("   SALTATO persona non esistente ")
            continue

        try:
            veicolo_id = ASSOC_ID_VEICOLI[iint(ferm[1])]
        except KeyError:
            print("   SALTATO veicolo non esistente ")
            continue

        inizio = data_da_timestamp(ferm[2])
        fine = data_da_timestamp(ferm[3], default=None)
        motivo = stringa(ferm[4]) or 'N/D'
        creazione = data_da_timestamp(ferm[6])
        ultima_modifica = data_da_timestamp(ferm[8], creazione)

        print("   %s fermo tecnico id=%d, veicolo=%d" % (
            progresso(contatore, totale), id, veicolo_id,
        ))

        f = FermoTecnico(
            motivo=motivo,
            veicolo_id=veicolo_id,
            creato_da_id=persona_id,
            inizio=inizio,
            fine=fine,
            creazione=creazione,
            ultima_modifica=ultima_modifica,
        )
        f.save()

    cursore.close()


def carica_tesserini():

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, stato,
            tipo, codice, timestamp,
            pRichiesta, tRichiesta, pConferma,
            tConferma, motivo, struttura,
            pRiconsegnato, tRiconsegnato
        FROM
            tesserinoRichiesta
        WHERE
            volontario IN (SELECT id FROM anagrafica)
        AND (pRichiesta IS NULL OR pRichiesta IN (SELECT id FROM anagrafica))
        AND (pConferma IS NULL OR pConferma IN (SELECT id FROM anagrafica))
        AND (pRiconsegnato IS NULL OR pRiconsegnato IN (SELECT id FROM anagrafica))
        """
    )

    tess = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for tes in tess:
        contatore += 1

        id = int(tes[0])

        try:
            persona_id = ASSOC_ID_PERSONE[iint(tes[1])]
        except KeyError:
            print("   SALTATO persona non esistente ")
            continue

        try:
            richiesto_da_id = ASSOC_ID_PERSONE[iint(tes[6])] if tes[6] else None
        except KeyError:
            print("   SALTATO pRichiesta non esistente ")
            continue

        try:
            confermato_da_id = ASSOC_ID_PERSONE[iint(tes[8])] if tes[8] else None
        except KeyError:
            print("   SALTATO pRichiesta non esistente ")
            continue

        try:
            riconsegnato_a_id = ASSOC_ID_PERSONE[iint(tes[12])] if tes[12] else None
        except KeyError:
            print("   SALTATO pRiconsegnato non esistente ")
            continue

        stato = int(tes[2])
        tipo = int(tes[3])
        codice = stringa(tes[4])

        creazione = data_da_timestamp(tes[5])
        tRichiesta = data_da_timestamp(tes[7])
        tConferma = data_da_timestamp(tes[9], default=None)
        motivo = stringa(tes[10])
        struttura = comitato_oid(tes[11])
        tRiconsegnato = data_da_timestamp(tes[13], default=None)

        if tipo == 0:
            tipo_richiesta = Tesserino.RILASCIO
        elif tipo == 10:
            tipo_richiesta = Tesserino.RINNOVO
        elif tipo == 20:
            tipo_richiesta = Tesserino.DUPLICATO
        else:
            raise ValueError("Tipo richiesta %d non aspettato" % (tipo,))

        stato_emissione = None
        if stato == 0:  # Rifiutato
            stato_richiesta = Tesserino.RIFIUTATO
            valido = False

        elif stato == 10:  # Richiesto
            stato_richiesta = Tesserino.RICHIESTO
            valido = False

        elif stato == 20:  # Stampato
            stato_richiesta = Tesserino.ACCETTATO
            stato_emissione = Tesserino.STAMPATO
            valido = True

        elif stato == 30:  # Spedito a casa
            stato_richiesta = Tesserino.ACCETTATO
            stato_emissione = Tesserino.SPEDITO_CASA
            valido = True

        elif stato == 40:  # Spedito in sede
            stato_richiesta = Tesserino.ACCETTATO
            stato_emissione = Tesserino.SPEDITO_SEDE
            valido = True

        elif stato == 50:  # Invalidato
            stato_richiesta = Tesserino.ACCETTATO
            stato_emissione = Tesserino.STAMPATO
            valido = False

        else:
            raise ValueError("Stato tesserino non aspettato: stato=%d" % (stato,))

        motivo_richiesta = ""
        motivo_rifiutato = ""

        if stato_richiesta == Tesserino.RIFIUTATO or (stato_emissione and not valido):
            motivo_rifiutato = motivo

        else:
            motivo_richiesta = motivo

        ultima_modifica = max([x for x in [creazione, tConferma, tRiconsegnato] if x is not None])

        t = Tesserino(
            persona_id=persona_id,
            emesso_da=struttura,
            tipo_richiesta=tipo_richiesta,
            stato_richiesta=stato_richiesta,
            motivo_richiesta=motivo_richiesta,
            motivo_rifiutato=motivo_rifiutato,
            stato_emissione=stato_emissione,
            valido=valido,
            codice=codice or None,
            richiesto_da_id=richiesto_da_id,
            confermato_da_id=confermato_da_id,
            data_conferma=tConferma,
            riconsegnato_a_id=riconsegnato_a_id,
            data_riconsegna=tRiconsegnato,
            creazione=creazione,
            ultima_modifica=ultima_modifica,
        )
        t.save()

        print("    %s tesserino codice=%s, persona_id=%d, emesso da=%s" % (
            progresso(contatore, totale), codice, persona_id, struttura,
        ))

    cursore.close()


def carica_gruppi():

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, comitato, nome,
            obiettivo, area, referente,
            attivita, estensione
        FROM
            gruppi
        WHERE
            comitato IS NOT NULL
        AND nome IS NOT NULL
        AND nome <> ''
        """
    )

    grp = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for gr in grp:
        contatore += 1

        id = int(gr[0])
        comitato = comitato_oid(gr[1])
        nome = stringa(gr[2])
        obiettivo = iint(gr[3], default=1)

        try:
            area_id = ASSOC_ID_AREE[int(gr[4])]
        except KeyError:
            print("   SALTATO area non esistente ")
            continue

        try:
            referente_id = ASSOC_ID_PERSONE[int(gr[5])] if gr[5] else None
        except KeyError:
            print("   SALTATO referente non esistente ")
            continue

        try:
            attivita_id = ASSOC_ID_ATTIVITA[int(gr[6])] if gr[6] else None
            attivita = Attivita.objects.get(pk=attivita_id) if attivita_id else None
        except KeyError:
            print("   SALTATO attivita non esistente ")
            continue

        g = gruppi.Gruppo(
            nome=nome,
            obiettivo=obiettivo,
            area_id=area_id,
            attivita_id=attivita_id,
            sede=comitato,
            estensione=comitato.estensione,
            creazione=attivita.creazione if attivita else timezone.now(),
            ultima_modifica=attivita.ultima_modifica if attivita else timezone.now(),
        )
        g.save()

        ASSOC_ID_GRUPPI[id] = g.pk

        if referente_id:
            referente = Persona.objects.get(pk=referente_id)
            g.aggiungi_delegato(REFERENTE_GRUPPO, referente, referente,
                                inizio=g.creazione)

        print("   %s gruppo sede=%s, area_id=%d, ref_id=%d, nome=%s" % (
            progresso(contatore, totale), comitato, area_id, referente_id or 0, nome,
        ))

    cursore.close()


def carica_gruppi_appartenenze():

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, gruppo,
            inizio, fine, timestamp,
            motivazione, tNega, pNega
        FROM
            gruppiPersonali
        WHERE
            volontario IS NOT NULL
        AND comitato IS NOT NULL
        """
    )

    apps = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for app in apps:
        contatore += 1

        id = int(app[0])

        try:
            persona_id = ASSOC_ID_PERSONE[iint(app[1])]
        except KeyError:
            print("   SALTATO persona non esistente ")
            continue

        try:
            pNega_id = ASSOC_ID_PERSONE[iint(app[8])] if app[8] else None
        except KeyError:
            print("   SALTATO pNega non esistente ")
            continue

        try:
            gruppo_id = ASSOC_ID_GRUPPI[iint(app[2])]
        except KeyError:
            print("   SALTATO Gruppo non esistente ")
            continue

        inizio = data_da_timestamp(app[3])
        fine = data_da_timestamp(app[4], default=None)
        creazione = data_da_timestamp(app[5])

        motivo_negazione = stringa(app[6]) or ''
        ultima_modifica = data_da_timestamp(app[7], default=creazione)

        a = gruppi.Appartenenza(
            gruppo_id=gruppo_id,
            persona_id=persona_id,
            motivo_negazione=motivo_negazione,
            inizio=inizio,
            fine=fine,
            negato_da_id=pNega_id,
            creazione=creazione,
            ultima_modifica=ultima_modifica
        )
        a.save()

        print("   %s app. gruppo, persona_id=%d, gruppo_id=%d" % (
            progresso(contatore, totale), persona_id, gruppo_id
        ))

    cursore.close()


def carica_dipendenti():

    print("  - Carico dipendenti")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, valore
        FROM
            dettagliPersona
        WHERE
            nome = 'dipendenteComitato'
        """
    )

    apps = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for app in apps:
        contatore += 1

        persid = ASSOC_ID_PERSONE[int(app[0])]
        comitato = comitato_oid(app[1])

        print("   %s dipendente persona_id=%d, sede=%s" % (
            progresso(contatore, totale), persid, comitato,
        ))

        a = Appartenenza(
            membro=Appartenenza.DIPENDENTE,
            persona_id=persid,
            sede=comitato,
            inizio=poco_fa(),
            fine=None,
        )
        a.save()

    cursore.close()


def carica_provvedimenti():

    print("  - Carico provvedimenti disciplinari")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, tipo, volontario,
            appartenenza, motivo, inizio,
            fine, protData, protNumero,
            pConferma, tConferma
        FROM
            provvedimenti

        """
    )

    provvs = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for pr in provvs:
        contatore += 1

        id = int(pr[0])
        tipo = int(pr[1])

        if tipo == 10:
            tipo = ProvvedimentoDisciplinare.AMMONIZIONE
        elif tipo == 20:
            tipo = ProvvedimentoDisciplinare.SOSPENSIONE
        elif tipo == 30:
            tipo = ProvvedimentoDisciplinare.ESPULSIONE
        else:
            print(tipo)
            raise ValueError("Tipo provvedimento non aspettato")

        persona_id = ASSOC_ID_PERSONE[int(pr[2])]
        try:
            app_id = ASSOC_ID_APPARTENENZE[int(pr[3])]
        except KeyError:
            print("   SALTATO appartenenza non esistente")
            continue

        sede = Appartenenza.objects.get(pk=app_id).sede
        motivo = stringa(pr[4])
        inizio = data_da_timestamp(pr[5])
        fine = data_da_timestamp(pr[6])
        protData = data_da_timestamp(pr[7])
        protNumero = stringa(pr[8])
        pConferma_id = ASSOC_ID_PERSONE[int(pr[9])]
        tConferma = data_da_timestamp(pr[10])

        print("   %s provvedimento id=%d, persona_id=%d, sede=%s" % (
            progresso(contatore, totale), id, persona_id, sede,
        ))

        p = ProvvedimentoDisciplinare(
            persona_id=persona_id,
            motivazione=motivo,
            sede=sede,
            inizio=inizio,
            fine=fine,
            protocollo_data=protData,
            protocollo_numero=protNumero,
            tipo=tipo,
            creazione=tConferma,
            ultima_modifica=tConferma,
            registrato_da_id=pConferma_id,
        )
        p.save()



    cursore.close()



def carica_dimissioni():

    print("  - Carico dimissioni")

    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, volontario, appartenenza,
            comitato, motivo, info,
            tConferma, pConferma
        FROM
            dimissioni
        WHERE
            appartenenza IS NOT NULL
        AND volontario IN (SELECT id FROM anagrafica)
        AND motivo IS NOT NULL
        """
    )

    dimm = cursore.fetchall()
    totale = cursore.rowcount
    contatore = 0

    for dim in dimm:
        contatore += 1

        id = int(dim[0])

        try:
            persona_id = ASSOC_ID_PERSONE[int(dim[1])]
        except KeyError:
            print("   SALTATO persona_id non esistente")
            continue

        try:
            pConferma_id = ASSOC_ID_PERSONE[int(dim[7])]
        except KeyError:
            print("   SALTATO pConferma_id non esistente")
            continue

        try:
            app_id = ASSOC_ID_APPARTENENZE[int(dim[2])]
        except KeyError:
            print("   SALTATO app_id non esistente")
            continue

        comitato = comitato_oid("Comitato:%d" % (int(dim[3]),))

        motivo = int(dim[4])

        if motivo == 10:
            motivo = Dimissione.VOLONTARIE
        elif motivo == 20:
            motivo = Dimissione.TURNO
        elif motivo == 25:
            motivo = Dimissione.RISERVA
        elif motivo == 30:
            motivo = Dimissione.QUOTA
        elif motivo == 40:
            motivo = Dimissione.RADIAZIONE
        elif motivo == 50:
            motivo = Dimissione.DECEDUTO
        else:
            raise ValueError("Valore motivo non aspettato %d" % (motivo,))

        info = stringa(dim[5])
        tConferma = data_da_timestamp(dim[6])

        print("   %s dimissione persona_id=%d, sede=%s" % (
            progresso(contatore, totale), persona_id, comitato
        ))

        d = Dimissione(
            persona_id=persona_id,
            appartenenza_id=app_id,
            sede=comitato,
            motivo=motivo,
            info=info,
            richiedente_id=pConferma_id,
            creazione=tConferma,
            ultima_modifica=tConferma,
        )
        d.save()

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

# Importazione degli Avatar
print("> Importazione degli Avatar")
if args.avatar:
    if not args.uploads:
        raise ValueError("Path non specificata. Usa --uploads.")

    print("  - Eliminazione attuali")
    Persona.objects.all().exclude(avatar__isnull=True).update(avatar=None)
    print("  - Importazione avatar (path: %s)" % (args.uploads,))
    carica_avatar()

# Importazione delle fototessere
print("> Importazione delle fototessere")
if args.fototessere:
    if not args.uploads:
        raise ValueError("Path non specificata. Usa --uploads.")

    print("  - Eliminazione attuali")
    Fototessera.objects.all().delete()
    print("  - Importazione fototessere (path: %s)" % (args.uploads,))
    carica_fototessere()

# Importazione dei documenti
print("> Importazione dei documenti")
if args.documenti:
    if not args.uploads:
        raise ValueError("Path non specificata. Usa --uploads.")

    print("  - Eliminazione attuali")
    Documento.objects.all().delete()
    print("  - Importazione documenti (path: %s)" % (args.uploads,))
    carica_documenti()

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
    carica_corsibase_assenze()
    carica_corsibase_partecipazioni()

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


# Importazione delle estensioni
print("> Importazione delle estensioni")
if args.estensioni:
    print("  - Eliminazione attuali")

    Estensione.objects.all().delete()
    carica_estensioni()

    print("  ~ Persisto tabella delle corrispondenze (estensioni.pickle-tmp)")
    pickle.dump(ASSOC_ID_ESTENSIONI, open("estensioni.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (estensioni.pickle-tmp)")
    ASSOC_ID_ESTENSIONI = pickle.load(open("estensioni.pickle-tmp", "rb"))


# Importazione del modulo autoparco
print("> Importazione modulo autoparco")
if args.veicoli:
    print("  - Eliminazione attuali")
    Veicolo.objects.all().delete()
    Collocazione.objects.all().delete()
    Autoparco.objects.all().delete()
    Rifornimento.objects.all().delete()
    Manutenzione.objects.all().delete()

    carica_autoparchi()
    carica_veicoli()
    carica_fermi_tecnici()
    carica_collocazioni()
    carica_rifornimenti()
    carica_manutenzioni()

    print("  ~ Persisto tabella delle corrispondenze (veicoli.pickle-tmp)")
    pickle.dump(ASSOC_ID_VEICOLI, open("veicoli.pickle-tmp", "wb"))
    print("  ~ Persisto tabella delle corrispondenze (autoparchi.pickle-tmp)")
    pickle.dump(ASSOC_ID_AUTOPARCHI, open("autoparchi.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (veicoli.pickle-tmp)")
    ASSOC_ID_VEICOLI = pickle.load(open("veicoli.pickle-tmp", "rb"))
    print("  ~ Carico tabella delle corrispondenze (autoparchi.pickle-tmp)")
    ASSOC_ID_AUTOPARCHI = pickle.load(open("autoparchi.pickle-tmp", "rb"))


# Importazione dei tesserini
print("> Importazione richieste di tesserino")
if args.tesserini:
    print("  - Eliminazione attuali")
    Tesserino.objects.all().delete()

    carica_tesserini()

    print("  ~ Persisto tabella delle corrispondenze (tesserini.pickle-tmp)")
    pickle.dump(ASSOC_ID_TESSERINI, open("tesserini.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (tesserini.pickle-tmp)")
    ASSOC_ID_TESSERINI = pickle.load(open("tesserini.pickle-tmp", "rb"))

# Importazione dei gruppi
print("> Importazione gruppi di lavoro")
if args.gruppi:
    print("  - Eliminazione attuali")
    gruppi.Gruppo.objects.all().delete()
    gruppi.Appartenenza.objects.all().delete()

    carica_gruppi()
    carica_gruppi_appartenenze()

else:
    print("  ~ Salto importazione dei gruppi di lavoro")


# Importazione dei dipendenti
print("> Importazione dei dipendenti")
if args.dipendenti:
    print("  - Eliminazione attuali")
    Appartenenza.objects.filter(membro=Appartenenza.DIPENDENTE).delete()
    carica_dipendenti()

else:
    print("  ~ Salto importazione dei dipendenti")


# Importazione dei provvedimenti disciplinari
print("> Importazione dei provvedimenti")
if args.provvedimenti:
    print("  - Eliminazione attuali")
    ProvvedimentoDisciplinare.objects.all().delete()

    carica_provvedimenti()

else:
    print("  ~ Salto importazione provvedimenti disciplinari")


print("> Importazione dei dimissioni")
if args.dimissioni:
    print("  - Eliminazione attuali")
    Dimissione.objects.all().delete()

    carica_dimissioni()

else:
    print("  ~ Salto importazione dimissioni")


print("> Importazione delle regole sulla privacy")
if args.privacy:
    print("  - Eliminazione attuali")
    #Priva.objects.all().delete()

    #carica_dimissioni()

else:
    print("  ~ Salto importazione dimissioni")



# print(ASSOC_ID_COMITATI)