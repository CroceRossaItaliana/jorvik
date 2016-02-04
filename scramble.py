# -*- coding: utf-8 -*-

import os, sys
import random

from anagrafica.permessi.applicazioni import PRESIDENTE

os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

import phonenumbers
from django.db import IntegrityError
from django.db.models import Count

from anagrafica.costanti import NAZIONALE, PROVINCIALE, TERRITORIALE
from autenticazione.models import Utenza
from base.utils import poco_fa
from base.utils_tests import crea_persona
from veicoli.models import Autoparco


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from anagrafica.models import Sede, Persona, Appartenenza, Delega
import argparse


__author__ = 'alfioemanuele'

parser = argparse.ArgumentParser(description='Mischia i dati anagrafici.')

parser.add_argument('--membri-sede', dest='membri_sedi', action='append',
                   help='dato pk di una sede, mischia i dati degli appartenenti passati e attuali')
parser.add_argument('--dati-di-esempio', dest='esempio', action='store_const',
                    default=False, const=True,
                    help='installa dei dati di esempio')

args = parser.parse_args()



def ottieni_random():  # Ottiene una persona a caso.
    numero = Persona.objects.aggregate(count=Count('id'))['count']
    while True:
        try:
            num = random.randint(0, numero - 1)
            p = Persona.objects.all()[num]
            return p
        except Persona.DoesNotExist:
            pass

def oscura(stringa, percentuale):
    out = ""
    for r in range(len(stringa)):
        out += stringa[r] if stringa[r] in ['@', '.'] or random.randint(0,100) > percentuale else chr(random.randint(64,90))
    return out

if args.membri_sedi:
    print("Avvio miscelatore anagrafico.")

for sede in (args.membri_sedi if args.membri_sedi else []):
    sede = Sede.objects.get(pk=sede)
    membri = Persona.objects.filter(appartenenze__sede__in=sede.get_descendants())
    totale = membri.count()
    print("Sede %s: Trovati %d membri." % (sede, totale,))
    contatore = 0

    for membro in membri:
        contatore += 1
        membro.nome = ottieni_random().nome
        membro.cognome = ottieni_random().cognome
        membro.save()

        tentativi_cf = 0
        while True:
            try:
                tentativi_cf += 1
                nuovo_codice_fiscale = oscura(ottieni_random().codice_fiscale, 50)
                membro.codice_fiscale = nuovo_codice_fiscale
                membro.save()
                break

            except IntegrityError:  # Riprova fino a che CF univoco
                pass

        tentativi_email_contatto = 0
        while True:
            try:
                tentativi_email_contatto += 1
                membro.email_contatto = oscura(ottieni_random().email_contatto, 35)
                membro.save()
                break

            except IntegrityError:  # Riprova fino a che CF univoco
                pass

        tentativi_utenza = 0
        try:
            if membro.utenza and not membro.utenza.is_staff:
                while True:
                    try:
                        tentativi_utenza += 1
                        utenza = membro.utenza
                        nuova_email = oscura(utenza.email, 75).lower()
                        utenza.email = nuova_email
                        utenza.save()
                        break

                    except IntegrityError:  # Riprova fino a che CF univoco
                        pass
        except:
            pass

        print("Miscelato %d di %d (%f percento): T.CF %d, T.EC %d, T.EU %d" % (
            contatore, totale, (contatore/totale*100), tentativi_cf, tentativi_email_contatto, tentativi_utenza)
        )

if args.esempio:
    print("Installo dei dati di esempio")

    print("Creo le Sedi fittizzie...")
    italia = Sede.objects.filter(estensione=NAZIONALE).first()
    c = Sede(nome="Comitato di Gaia", genitore=italia, estensione=PROVINCIALE)
    c.save()
    s1 = Sede(nome="York", genitore=c, estensione=TERRITORIALE)
    s1.save()
    s2 = Sede(nome="Bergamo", genitore=c, estensione=TERRITORIALE)
    s2.save()
    s3 = Sede(nome="Catania", genitore=c, estensione=TERRITORIALE)
    s3.save()
    a1 = Autoparco(nome="Autorimessa Principato", sede=s3)
    a1.save()

    print("Genero dei membri della Sede a caso...")
    for sede in [c, s1, s2, s3]:  # Per ogni Sede
        for membro in [Appartenenza.VOLONTARIO, Appartenenza.SOSTENITORE]:
            for i in range(0, 20):  # Creo 20 volontari
                p = crea_persona()
                a = Appartenenza(persona=p, sede=sede, inizio=poco_fa(), membro=membro)
                a.save()

    print("Ne creo un presidente...")
    # Creo il presidente
    presidente = crea_persona()
    presidente.nome = "Douglas"
    presidente.cognome = "Adams"
    presidente.save()

    a = Appartenenza(persona=presidente, sede=s1, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)
    a.save()

    # Assegno una utenza
    print(" - Creo credenziali...")
    utenza = Utenza(persona=presidente, email="supporto@gaia.cri.it",
                    password='pbkdf2_sha256$20000$ldk8aPLgcMXK$Cwni1ubmmKpzxO8xM75ZuwNR+k6ZHA5JTVxJFbgIzgo=')
    utenza.save()

    # Assegno una delelga presidente
    print(" - Nomino presidente")
    d = Delega(persona=presidente, tipo=PRESIDENTE, oggetto=c, inizio=poco_fa())
    d.save()

    print("= Fatto.")


print("Finita esecuzione.")
