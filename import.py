import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

import pickle
from django.contrib.gis.geos import Point
from autenticazione.models import Utenza


from safedelete import HARD_DELETE
from jorvik.settings import MYSQL_CONF

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.template.backends import django
from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from anagrafica.models import Sede, Persona
from base.geo import Locazione
import argparse

from datetime import datetime

__author__ = 'alfioemanuele'

import MySQLdb

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
parser.add_argument('--ignora-errori-db', dest='ignora', action='store_const',
                   const=True, default=False,
                   help='ignora errori di integrità (solo test)')

args = parser.parse_args()


# .conect(host, username, password, database)
db = MySQLdb.connect(
    MYSQL_CONF.get('client', 'host'),
    MYSQL_CONF.get('client', 'user'),
    MYSQL_CONF.get('client', 'password'),
    MYSQL_CONF.get('client', 'database')
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
#  es. ASSOC_ID['123'] = 4422
ASSOC_ID_PERSONE = {}

def ottieni_comitato(tipo='nazionali', id=1):
    cursore = db.cursor()
    cursore.execute("""
        SELECT
            id, nome, X(geo), Y(geo)
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

def data_da_timestamp(timestamp, default=datetime.now()):
    if not timestamp:
        return default
    timestamp = int(timestamp)
    try:
        return datetime.fromtimestamp(timestamp)
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

    totale = str(cursore.rowcount)
    contatore = 0
    for persona in persone:

        contatore += 1

        if args.verbose:
            print("    - " + str(contatore) + " su " + totale + ": id=" + str(persona[0]) + ", codice_fiscale=" + str(persona[6]))
            print("      - Scaricamento dati aggiuntivi")

        id = persona[0]

        dict = DETTAGLI_DICT.get(int(persona[0]), {})
        dati = {
            'id': persona[0],
            'nome': persona[1],
            'cognome': persona[2],
            'stato': persona[3],
            'email': persona[4],
            'password': persona[5],
            'codiceFiscale': persona[6],
            'timestamp': persona[7],
            'admin': persona[8],
            'consenso': persona[9],
            'sesso': persona[10],
            'dettagliPersona': dict
        }

        #print(dati)
        if args.verbose:
            print("      - Creazione della scheda anagrafica")

        p = Persona(
            nome=dati['nome'],
            cognome=dati['cognome'],
            codice_fiscale=dati['codiceFiscale'],
            data_nascita=data_da_timestamp(dict.get('dataNascita'), default=None),
            genere=Persona.MASCHIO if dati['sesso'] == 1 else Persona.FEMMINA,
            stato=Persona.PERSONA,
            comune_nascita=dict.get('comuneNascita'),
            provincia_nascita=dict.get('provinciaNascita')[0:2] if dict.get('provinciaNascita') else None,
            stato_nascita='IT',
            indirizzo_residenza=str(dict.get('indirizzo')) + ", " + str(dict.get('civico')),
            comune_residenza=dict.get('comuneResidenza'),
            provincia_residenza=dict.get('provinciaResidenza')[0:2] if dict.get('provinciaResidenza') else None,
            stato_residenza='IT',
            cap_residenza=dict.get('CAPResidenza'),
            email_contatto=dict.get('emailServizio', ''),
            creazione=data_da_timestamp(dict.get('timestamp')),
        )
        try:
            p.save()
        except:
            if args.ignora:
                print("    ERRORE DATABASE IGNORATO")
                continue
            else:
                raise

        if dati['email']:
            if args.verbose:
                print("      - Utenza attiva " + str(dati['email']))
            u = Utenza(
                persona=p,
                ultimo_accesso=datetime.fromtimestamp(int(dict.get('ultimoAccesso', None))) if dict.get('ultimoAccesso', None) else None,
                ultimo_consenso=datetime.fromtimestamp(int(dati['consenso'])) if dati['consenso'] else None,
                email=dati['email'],
                is_staff=True if dati['admin'] else False
            )
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
                print("      - Numero cellulare personale " + str(dict.get('cellulare')))
            p.aggiungi_numero_telefono(dict.get('cellulare'), False)

        if dict.get('cellulareServizio', False):
            if args.verbose:
                print("      - Numero cellulare servizio " + str(dict.get('cellulareServizio')))
            p.aggiungi_numero_telefono(dict.get('cellulareServizio'), True)

        ASSOC_ID_PERSONE.update({int(id): p.pk})
        # print(dict.keys())



def locazione(geo, indirizzo):
    if not indirizzo:
        return None
    try:
        l = Locazione.objects.get(indirizzo=indirizzo)
    except:
        l = Locazione(geo=geo, indirizzo=indirizzo)
        l.save()
    return l

def carica_comitato(posizione=True, tipo='nazionali', id=1, ref=None, num=0):

    comitato = ottieni_comitato(tipo, id)

    c = Sede(
        genitore=ref,
        nome=comitato['nome'],
        tipo=Sede.COMITATO,
        estensione=COMITATO_ESTENSIONE[tipo],
    )
    c.save()

    ASSOC_ID_COMITATI[COMITATO_OID[tipo]].update({id: (Sede, c.pk)})

    if posizione and 'formattato' in comitato['dati'] and comitato['dati']['formattato']:
        c.imposta_locazione(comitato['dati']['formattato'])

    if args.verbose:
        print("    - " + ("-"*num) + " " + c.nome + ": " + str(c.locazione))

    totale = 1
    for (a, b) in ottieni_figli(tipo,id):
        totale += carica_comitato(posizione, a, b, c, num+1)

    return totale


# Importazione dei Comitati

print("> Importazione dei Comitati")

if args.comitati:
    print("  - Eliminazione attuali")
    Sede.objects.all().delete()
    print("  - Importazione dal database, geolocalizzazione " + str("attiva" if args.geo else "disattiva"))

    try:
        n = carica_comitato(args.geo)
    except KeyboardInterrupt:
        print("Saltato")
        n = 0
    print("  = Importati " + str(n) + " comitati.")
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
    print("  - Importazione dal database")
    carica_anagrafiche()
    print("  ~ Persisto tabella delle corrispondenze (persone.pickle-tmp)")
    pickle.dump(ASSOC_ID_PERSONE, open("persone.pickle-tmp", "wb"))

else:
    print("  ~ Carico tabella delle corrispondenze (persone.pickle-tmp)")
    ASSOC_ID_PERSONE = pickle.load(open("persone.pickle-tmp", "rb"))

# print(ASSOC_ID_COMITATI)