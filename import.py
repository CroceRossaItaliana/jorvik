# coding=utf8

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
from anagrafica.permessi.applicazioni import PRESIDENTE, DELEGATO_AREA, REFERENTE, DELEGATO_OBIETTIVO_1, \
    DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, \
    DELEGATO_CO, UFFICIO_SOCI, RESPONSABILE_PATENTI, RESPONSABILE_FORMAZIONE, UFFICIO_SOCI_TEMPORANEO, \
    RESPONSABILE_AUTOPARCO, RESPONSABILE_DONAZIONI
from attivita.models import Area, Attivita, Partecipazione, Turno
from base.models import Autorizzazione

import pickle
from django.contrib.gis.geos import Point
from autenticazione.models import Utenza


from safedelete import HARD_DELETE
from jorvik.settings import MYSQL_CONF

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.template.backends import django
from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from anagrafica.models import Sede, Persona, Appartenenza, Delega
from base.geo import Locazione
import argparse

from datetime import datetime, date

__author__ = 'alfioemanuele'

import MySQLdb

def stringa(s):
    if s is None:
        return ''
    # try:
    #    #return str(s.encode('utf-8'))
    #except:
    return str(s)

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


def progresso(contatore, totale):
    percentuale = contatore / float(totale) * 100.0
    return "%.2f%% (%d su %d) " % (percentuale, contatore, totale)

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
    if not timestamp:  # timestamp 0, 1970-1-1
        return default
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
            'nome': persona[1],
            'cognome': persona[2],
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

        provincia_residenza = dict.get('provinciaResidenza')[0:2] if dict.get('provinciaResidenza') else ''
        provincia_nascita = dict.get('provinciaNascita')[0:2] if dict.get('provinciaNascita') else provincia_residenza
        data_nascita = data_da_timestamp(dict.get('dataNascita'), default=None)
        p = Persona(
            nome=dati['nome'],
            cognome=dati['cognome'],
            codice_fiscale=dati['codiceFiscale'],
            data_nascita=data_nascita,
            genere=Persona.MASCHIO if dati['sesso'] == 1 else Persona.FEMMINA,
            stato=Persona.PERSONA,
            comune_nascita=dict.get('comuneNascita') if dict.get('comuneNascita') else '',
            provincia_nascita=provincia_nascita,
            stato_nascita='IT',
            indirizzo_residenza=stringa(dict.get('indirizzo')) + ", " + stringa(dict.get('civico')),
            comune_residenza=dict.get('comuneResidenza') if dict.get('comuneResidenza') else '',
            provincia_residenza=provincia_residenza,
            stato_residenza='IT',
            cap_residenza=dict.get('CAPResidenza') if dict.get('CAPResidenza') else '',
            email_contatto=dict.get('emailServizio', ''),
            creazione=data_da_timestamp(dict.get('timestamp')),
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
            continue

        if stato in [5, 14, 15, 25, 35]:
            membro = Appartenenza.ESTESO

        elif stato in [0, 1, 3, 9, 10, 20, 30, 40, 50, 60, 70, 80]:
            membro = Appartenenza.VOLONTARIO

        elif stato in [2, 4, 16]:
            membro = Appartenenza.ORDINARIO

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
                ((PRESIDENTE, comitato)),
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
                motivo_obbligatorio=False,
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


# print(ASSOC_ID_COMITATI)