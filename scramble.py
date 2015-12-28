# -*- coding: utf-8 -*-

import os, sys
import random

import phonenumbers
from django.db import IntegrityError
from django.db.models import Count

os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from anagrafica.models import Sede, Persona

import argparse


__author__ = 'alfioemanuele'

parser = argparse.ArgumentParser(description='Mischia i dati anagrafici.')

parser.add_argument('--membri-sede', dest='membri_sedi', action='append',
                   help='dato pk di una sede, mischia i dati degli appartenenti passati e attuali')

args = parser.parse_args()

print("Avvio miscelatore anagrafico.")


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

        print("Miscelato %d di %d (%f percento): T.CF %d, T.EC %d, T.EU %d" % (
            contatore, totale, (contatore/totale*100), tentativi_cf, tentativi_email_contatto, tentativi_utenza)
        )

print("Finita esecuzione.")
