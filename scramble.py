#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import math
import argparse
from datetime import timedelta

from django.db import transaction, IntegrityError
from django.db.models import Count
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'
application = get_wsgi_application()

from anagrafica.models import Sede, Persona, Appartenenza, Delega, Trasferimento, Estensione
from anagrafica.permessi.applicazioni import (PRESIDENTE, UFFICIO_SOCI,
    DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, RESPONSABILE_FORMAZIONE, DIRETTORE_CORSO)
from anagrafica.costanti import NAZIONALE, TERRITORIALE, REGIONALE, LOCALE, PROVINCIALE
from autenticazione.models import Utenza
from attivita.models import Attivita, Area
from base.comuni import COMUNI
from base.utils import poco_fa, oggi
from base.utils_tests import crea_persona, email_fittizzia, codice_fiscale_persona
from base.geo import Locazione
from posta.models import Messaggio
from veicoli.models import Autoparco, Collocazione


t_deleted = Trasferimento.objects.filter().delete()
a_deleted = Appartenenza.objects.filter().delete()
p_deleted = Persona.objects.filter().delete()

print("Eliminati seguenti records dal db: Trasferimento: %s - Appartenenza: %s - Persona: %s" % (t_deleted[0], a_deleted[0], p_deleted[0]))


parser = argparse.ArgumentParser(description='Mischia i dati anagrafici.')
parser.add_argument('--membri-sede', dest='membri_sedi', action='append',
                   help='dato pk di una sede, mischia i dati degli appartenenti passati e attuali')
parser.add_argument('--dati-di-esempio', dest='esempio', action='store_const',
                    default=False, const=True,
                    help='installa dei dati di esempio')
parser.add_argument('--email-di-esempio', dest='email', type=int, default=0,
                    help='installa delle email di esempio per test coda celery')
parser.add_argument('--reset', dest='reset', action='store_true',
                    help='cancella i dati prima di caricare quelli di esempio. Funziona solo con --dati-di-esempio')
parser.add_argument('--aggiorna-province', dest='province', action='store_const',
                    default=False, const=True,
                    help='aggiorna le province')
args = parser.parse_args()


# Creare utente con i privilegi di superuser
superuser = Utenza.objects.create_superuser('provami@provami.gaia.cri.it',
                                            'hZ4hK5uL5tE8gG2u')
if superuser:
    print("Utente <%s> con privilegi di superuser creato."  % str(superuser))


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

def provami_rename_test_user(persona, indice, delega_tipo):
    from anagrafica.permessi.applicazioni import PERMESSI_NOMI

    permesso_full_name = dict(PERMESSI_NOMI)[locals()['delega_tipo']]

    pr_nome = "%s_%s" % ('_'.join(permesso_full_name.split()).lower(), indice)
    for _char in ['(', ')']:
        pr_nome = pr_nome.replace(_char, '').strip()

    pr_email = "%s@cri.it" % pr_nome

    utenza = persona.utenza
    utenza.email = pr_email
    utenza.set_password(pr_email)
    utenza.save()

    persona.nome = pr_nome
    persona.cognome = pr_nome
    persona.save()

    return utenza, persona

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

    if args.reset:
        print("Cancello i dati esistenti come richiesto")
        with transaction.atomic():
            from formazione.models import CorsoBase, LezioneCorsoBase, PartecipazioneCorsoBase
            Collocazione.objects.all().delete()
            PartecipazioneCorsoBase.objects.all().delete()
            LezioneCorsoBase.objects.all().delete()
            CorsoBase.objects.all().delete()
            Trasferimento.objects.all().delete()
            Utenza.objects.all().delete()
            Attivita.objects.all().delete()
            Area.objects.all().delete()
            Persona.objects.all().delete()
            Appartenenza.objects.all().delete()
            Delega.objects.all().delete()
            Sede.objects.all().delete()

    print("Creo le Sedi fittizie...")
    italia = Sede.objects.create(nome="Comitato Nazionale", estensione=NAZIONALE)
    regionale = Sede.objects.create(nome="Comitato Regione 1", estensione=REGIONALE, genitore=italia)
    metropolitano = Sede.objects.create(nome="Comitato Metropolitano 1", estensione=PROVINCIALE, genitore=regionale)
    altra_regione = Sede.objects.create(nome="Comitato Regione 2", estensione=REGIONALE, genitore=italia)
    c = Sede.objects.create(nome="Comitato di Gaia", genitore=regionale, estensione=LOCALE)
    s1 = Sede.objects.create(nome="York", genitore=c, estensione=TERRITORIALE)
    s2 = Sede.objects.create(nome="Bergamo", genitore=c, estensione=TERRITORIALE)
    s3 = Sede.objects.create(nome="Catania", genitore=c, estensione=TERRITORIALE)
    c2 = Sede.objects.create(nome="Altro Comitato di Gaia", genitore=altra_regione, estensione=LOCALE)
    c3 = Sede.objects.create(nome="Comitato Fittizio", genitore=regionale, estensione=LOCALE)
    cm1 = Sede.objects.create(nome="Comitato 1 sotto Metropolitano", genitore=metropolitano, estensione=LOCALE)
    cm2 = Sede.objects.create(nome="Comitato 2 sotto Metropolitano", genitore=metropolitano, estensione=LOCALE)
    a1 = Autoparco(nome="Autorimessa Principato", sede=s3)
    a1.save()

    presidente = None

    print("Genero dei membri della Sede a caso con deleghe e cariche ...")
    print(" - Creo persone...")
    sedi = [c, s1, s2, s3, c2, c3, regionale, metropolitano, altra_regione, cm1, cm2]
    nuove = []

    test_volontario = None
    test_presidente = None
    test_resp_formazione = None
    test_direttore_corso = None
    test_delegato_obiettivo = None

    for sede in sedi:  # Per ogni Sede
        locazione = Locazione.oggetto(indirizzo=random.sample(COMUNI.keys(), 1)[0])
        sede.locazione = locazione
        sede.save()

        if sede.estensione == REGIONALE:
            tipi = [Appartenenza.VOLONTARIO, Appartenenza.SOSTENITORE, Appartenenza.ORDINARIO]
        else:
            tipi = [Appartenenza.VOLONTARIO, Appartenenza.SOSTENITORE]

        for membro in tipi:
            for i in range(0, 25):  # Creo 20 volontari
                p = crea_persona()
                p.comune_nascita = random.sample(COMUNI.keys(), 1)[0]
                p.genere = random.choice((p.MASCHIO, p.FEMMINA))
                p.indirizzo_residenza = 'Via prova 34'
                p.comune_residenza = random.sample(COMUNI.keys(), 1)[0]
                p.provincia_residenza = 'ZZ'
                p.cap_residenza = '00100'
                p.codice_fiscale = codice_fiscale_persona(p)
                p.save()
                nuove.append(p)
                data = poco_fa() - timedelta(days=random.randint(10, 5000))
                a = Appartenenza.objects.create(persona=p, sede=sede, inizio=data, membro=membro)

                if membro == Appartenenza.VOLONTARIO:
                    if membro == Appartenenza.VOLONTARIO and test_volontario is None:
                        test_volontario = p

                    if i % 5 == 0:
                        # Dimesso e riammesso
                        data_precedente = data - timedelta(days=random.randint(10, 500))
                        altra = random.sample(sedi, 1)[0]
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra, inizio=data_precedente, fine=data, membro=membro,
                            terminazione=Appartenenza.DIMISSIONE
                        )
                    if i % 5 == 1:
                        # Trasferimento nel passato
                        data_precedente = data - timedelta(days=random.randint(10, 500))
                        altra = random.sample(sedi, 1)[0]
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra, inizio=data_precedente, fine=data, membro=membro,
                            terminazione=Appartenenza.TRASFERIMENTO
                        )
                        Trasferimento.objects.create(
                            richiedente=p, persona=p, destinazione=altra, appartenenza=a,
                            protocollo_numero=1, protocollo_data=data_precedente, motivo='motivo'
                        )
                    if i % 5 == 3:
                        # Catena di trasferimenti
                        data_precedente = data - timedelta(days=random.randint(10, 500))
                        altra = random.sample(sedi, 1)[0]
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra, inizio=data_precedente, fine=data, membro=membro,
                            terminazione=Appartenenza.TRASFERIMENTO
                        )
                        Trasferimento.objects.create(
                            richiedente=p, persona=p, destinazione=altra, appartenenza=a,
                            protocollo_numero=1, protocollo_data=data_precedente, motivo='motivo'
                        )
                        data_precedente_vecchia = data_precedente - timedelta(days=random.randint(10, 500))
                        altra = random.sample(sedi, 1)[0]
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra, inizio=data_precedente_vecchia, fine=data_precedente, membro=membro,
                            terminazione=Appartenenza.TRASFERIMENTO
                        )
                        Trasferimento.objects.create(
                            richiedente=p, persona=p, destinazione=altra, appartenenza=a,
                            protocollo_numero=1, protocollo_data=data_precedente_vecchia, motivo='motivo'
                        )
                        # Catena di estensioni su appartenenza corrente
                        data_est_1 = data + timedelta(days=math.floor((poco_fa() - data).days/2))
                        fine_est_1 = poco_fa()
                        data_est_2 = data + timedelta(days=math.floor((poco_fa() - data).days/3))
                        altra = random.sample(sedi, 1)[0]
                        altra_2 = random.sample(sedi, 1)[0]
                        a = Appartenenza.objects.create(
                            persona=p, sede=c, inizio=data_est_1, membro=Appartenenza.ESTESO, fine=fine_est_1,
                            terminazione=Appartenenza.FINE_ESTENSIONE
                        )
                        Estensione.objects.create(
                            richiedente=p, persona=p, destinazione=altra, appartenenza=a,
                            protocollo_numero=1, protocollo_data=data_est_1, motivo='motivo'
                        )
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra, inizio=data_est_1, membro=Appartenenza.ESTESO, fine=fine_est_1,
                            terminazione=Appartenenza.FINE_ESTENSIONE
                        )
                        Estensione.objects.create(
                            richiedente=p, persona=p, destinazione=altra, appartenenza=a,
                            protocollo_numero=1, protocollo_data=data_est_1, motivo='motivo'
                        )
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra_2, inizio=data_est_2, membro=Appartenenza.ESTESO,
                        )
                        Estensione.objects.create(
                            richiedente=p, persona=p, destinazione=altra_2, appartenenza=a,
                            protocollo_numero=1, protocollo_data=data_est_2, motivo='motivo'
                        )
                    if i % 5 == 2:
                        # Espulso e riammesso
                        data_precedente = data - timedelta(days=random.randint(10, 500))
                        data_fine = data - timedelta(days=math.floor((data - data_precedente).days/2))
                        altra = random.sample(sedi, 1)[0]
                        a = Appartenenza.objects.create(
                            persona=p, sede=altra, inizio=data_precedente, fine=data_fine, membro=membro,
                            terminazione=Appartenenza.ESPULSIONE
                        )

        for i in range(0, 15):  # Creo 15 aspiranti
            try:
                p = crea_persona()
                p.comune_nascita = random.sample(COMUNI.keys(), 1)[0]
                p.codice_fiscale = codice_fiscale_persona(p)  # puo failire qui
                p.save()
                p.ottieni_o_genera_aspirante()
                email = email_fittizzia()
                utenza = Utenza.objects.create_user(
                    persona=p, email=email,
                    password=email
                )
            except KeyError:
                """ chiamata codice_fiscale_persona() fallisce con: KeyError: '.' 
                Non creare aspirante/utente.
                """
                print("--- Errore creazione aspirante e utenza. Iterazione %s" % i)

        if sede.estensione in (LOCALE, REGIONALE, PROVINCIALE):
            print(" - Assegno deleghe...")
            persone = [a.persona for a in Appartenenza.objects.filter(sede=sede, membro=Appartenenza.VOLONTARIO).order_by('?')[:6]]
            for indice, persona in enumerate(persone):
                if indice == 0:
                    d = Delega.objects.create(persona=persona, tipo=PRESIDENTE, oggetto=sede, inizio=poco_fa())
                    if sede == c:
                        # Grazie per tutto il pesce
                        persona.nome = "Douglas"
                        persona.cognome = "Adams"
                        persona.codice_fiscale = codice_fiscale_persona(persona)
                        persona.save()
                        presidente = persona

                        # Assegno una utenza
                        if not Utenza.objects.filter(email="supporto@gaia.cri.it").exists():
                            utenza = Utenza.objects.create(
                                persona=persona, email="supporto@gaia.cri.it",
                                password='pbkdf2_sha256$24000$vuuP6g3dJTyz$55k2PL/NCVk2j4T+cvA9pGeIkFRT2lxKMbjFLZeYR3Y='
                            )

                        provami_rename_test_user(persona, indice, delega_tipo=PRESIDENTE)

                elif indice == 1:
                    d = Delega.objects.create(persona=persona, tipo=UFFICIO_SOCI, oggetto=sede, inizio=poco_fa())

                elif indice == 2:
                    d = Delega.objects.create(persona=persona, tipo=DELEGATO_OBIETTIVO_1, oggetto=sede, inizio=poco_fa())
                    if test_delegato_obiettivo is None:
                        test_delegato_obiettivo = persona

                elif indice == 3:
                    d = Delega.objects.create(persona=persona, tipo=DELEGATO_OBIETTIVO_2, oggetto=sede, inizio=poco_fa())

                elif indice == 4:
                    if test_resp_formazione is None:
                        test_resp_formazione = persona
                        d = Delega.objects.create(persona=persona, tipo=RESPONSABILE_FORMAZIONE, oggetto=sede, inizio=poco_fa())

                elif indice == 5:
                    if test_direttore_corso is None:
                        from formazione.models import CorsoBase

                        test_direttore_corso = persona
                        #corso = CorsoBase.nuovo(sede=sede, data_inizio=poco_fa(), data_esame=poco_fa())
                        #d = Delega.objects.create(persona=persona, tipo=DIRETTORE_CORSO, oggetto=corso, inizio=poco_fa())

    print(" - Creo utenze di accesso...")
    for idx, persona in enumerate(nuove):
        try:
            email = email_fittizzia()
            utenza = Utenza.objects.create_user(persona=persona, email=email, password=email)

            ###
            # Creazione utenze per tests (di Andrea)
            ###
            if persona == test_volontario:
                vo_nome ='volontario_%s' % idx
                vo_email = vo_nome + "@cri.it"

                utenza.email = vo_email
                utenza.set_password(vo_email)
                utenza.save()

                persona.nome = vo_nome
                persona.cognome = vo_nome
                persona.save()
                persona.refresh_from_db()

            elif persona == test_resp_formazione:
                provami_rename_test_user(persona, idx, delega_tipo=RESPONSABILE_FORMAZIONE)

            elif persona == test_direttore_corso:
                provami_rename_test_user(persona, idx, delega_tipo=DIRETTORE_CORSO)

            elif persona == test_delegato_obiettivo:
                provami_rename_test_user(persona, idx, delega_tipo=DELEGATO_OBIETTIVO_1)

        except IntegrityError:
            print('  --- Errore creazione utenza per {}'.format(persona))

    print("= Fatto.")

if args.province:
    print("Aggiorno le province")

    province = Locazione.objects.filter(stato="IT").exclude(provincia='').values_list('provincia', flat=True).distinct()

    for provincia in province:
        prima = Locazione.objects.filter(provincia=provincia).first()
        prima.cerca_e_aggiorna()
        pv = prima.provincia_breve

        altre = Locazione.objects.filter(provincia=provincia)
        num = altre.update(provincia_breve=pv)

        print("-- %s\t%d\t%s" % (pv, num, provincia))

if args.email:
    print("Installo emails di esempio")
    # setup di celery per poter accodare
    from jorvik.celery import app

    if args.reset:
        Messaggio.objects.all().delete()

    persone = iter(Persona.objects.all().order_by('?'))
    for n in range(args.email):
        try:
            mittente = next(persone)
            destinatari = [next(persone) for _ in range(random.randint(0, 5))]
            job = Messaggio.costruisci_e_accoda(oggetto='Prova email numero {}'.format(n + 1),
                                                modello='test_email.html',
                                                mittente=mittente,
                                                destinatari=destinatari)
        except StopIteration:
            persone = iter(Persona.objects.all().order_by('?')) # rewind

print("Finita esecuzione.")
