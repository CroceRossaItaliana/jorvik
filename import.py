import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

from django.db import transaction, IntegrityError
from anagrafica.permessi.applicazioni import PRESIDENTE, DELEGATO_AREA, REFERENTE
from attivita.models import Area, Attivita

import pickle
from django.contrib.gis.geos import Point
from autenticazione.models import Utenza


from safedelete import HARD_DELETE
from jorvik.settings import MYSQL_CONF

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.template.backends import django
from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from anagrafica.models import Sede, Persona, Appartenenza
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
parser.add_argument('--salta-appartenenze', dest='appartenenze', action='store_const',
                   const=False, default=True,
                   help='salta importazione appartenenze (usa cache precedente)')
parser.add_argument('--salta-aree', dest='aree', action='store_const',
                   const=False, default=True,
                   help='salta importazione aree (usa cache precedente)')
parser.add_argument('--salta-attivita', dest='attivita', action='store_const',
                   const=False, default=True,
                   help='salta importazione attivita (usa cache precedente)')
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

# Questo dizionario mantiene le associazioni ID delle aree
#  es. ASSOC_ID_AREE[123] = 444
ASSOC_ID_AREE = {}

# Questo dizionario mantiene le associazioni ID delle attivita
#  es. ASSOC_ID_ATTIVITA[123] = 465
ASSOC_ID_ATTIVITA = {}


def progresso(contatore, totale):
    percentuale = contatore / totale * 100.0
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
            print("    - " + progresso(contatore, totale) + ": id=" + str(persona[0]) + ", codice_fiscale=" + str(persona[6]))
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
        except IntegrityError:
            if args.verbose:
                print("    - CF DUPLICATO: Unione...")
                p = Persona.objects.get(codice_fiscale=dati['codiceFiscale'])

        # Se anagrafica attiva (ha accesso), crea Utenza
        if dati['email']:

            if args.verbose:
                print("      - Utenza attiva " + str(dati['email']))

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
                print("      - Numero cellulare personale " + str(dict.get('cellulare')))
            p.aggiungi_numero_telefono(dict.get('cellulare'), False)

        if dict.get('cellulareServizio', False):
            if args.verbose:
                print("      - Numero cellulare servizio " + str(dict.get('cellulareServizio')))
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
            print("    - " + progresso(contatore, totale) + ": Appartenenza id=" + str(id))

        persona = int(app[1])
        comitato = int(app[2])

        if persona not in ASSOC_ID_PERSONE:
            if args.verbose:
                print("      IGNORATA: Persona non riconosciuta (id=" + str(persona) + ")")
            continue
        persona = ASSOC_ID_PERSONE[persona]
        persona = Persona.objects.get(pk=persona)

        if comitato not in ASSOC_ID_COMITATI['Comitato']:
            if args.verbose:
                print("      IGNORATA: Comitato non riconosciuto (id=" + str(comitato) + ")")
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
                print("      IGNORATA: Stato appartenenza non riconosciuto (stato=" + str(stato) + ")")
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
    oid = str(oid)
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

@transaction.atomic
def carica_comitati(geo):
    with Sede.objects.delay_mptt_updates():
        n = carica_comitato(geo)
        print("  - Persisto su database...")
    return n

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
        nome = str(area[1])
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
                print("      - Aggiunta delegato, persona=%s" % (str(responsabile), ))

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
        nome = str(att[1])
        luogo = str(att[2])
        comitato = comitato_oid(att[3])
        estensione = comitato_estensione(comitato, int(att[4]))
        referente = persona_id(att[5])
        descrizione = str(att[7])
        stato = Attivita.BOZZA if int(att[8]) == 10 else Attivita.VISIBILE
        area = area_id(att[9])

        if att[10] is None:
            apertura = Attivita.CHIUSA
        else:
            apertura = Attivita.APERTA if int(att[10]) == 10 else Attivita.CHIUSA

        if args.verbose:
            print("    - " + progresso(contatore, totale) + "Attivita: id=%s, comitato=%s, nome=%s" % (id, att[3], nome))

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
                print("      - Impostato luogo: " + str(l))

        if referente:
            a.aggiungi_delegato(REFERENTE, referente)
            if args.verbose:
                print("      - Impostato referente: " + str(referente))

        ASSOC_ID_ATTIVITA[id] = a.pk




# Importazione dei Comitati

print("> Importazione dei Comitati")

if args.comitati:
    print("  - Eliminazione attuali")
    Sede.objects.all().delete()
    print("  - Importazione dal database, geolocalizzazione " + str("attiva" if args.geo else "disattiva"))
    n = carica_comitati(args.geo)
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


# Importazione delle Aree
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


# print(ASSOC_ID_COMITATI)