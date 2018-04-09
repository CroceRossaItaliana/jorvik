# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import string

from django.template.loader import get_template
from django.utils.crypto import random
from django.utils.timezone import now

from anagrafica.models import Persona, Delega
from anagrafica.permessi.applicazioni import DELEGATO_OBIETTIVO_5
from base.utils import mezzanotte_24_ieri
from posta.models import Messaggio


def _richiesta_conferma_email(request, me, parametri, modulo):
    email = modulo.cleaned_data.get(parametri['field'], None)
    if email and email != parametri['precedente']:
        request.session[parametri['session_code']] = email
        corpo = {
            'code': request.session[parametri['session_key']],
            'code_type': parametri['code_type'],
            'vecchia_email': parametri['precedente'],
            'nuova_email': email,
            'persona': me,
            'autore': me,
        }
        Messaggio.invia_raw(
            oggetto=parametri['oggetto'],
            corpo_html=get_template(parametri['template']).render(corpo),
            email_mittente=None,
            lista_email_destinatari=[
                email
            ]
        )


def _conferma_email(request, me, parametri):
    stato_conferma, errore_conferma = False, False
    nuova_email = request.session.get(parametri['session_code'], '')
    if nuova_email and nuova_email != parametri['precedente'] and request.session.get(parametri['session_key']):
        if request.session.get(parametri['session_key']) != request.GET.get(parametri['code_type'], None):
            errore_conferma = True
        else:
            if parametri['code_type'] == 'code_m':
                me.utenza.email = nuova_email
                me.utenza.save()
            elif parametri['code_type'] == 'code_c':
                me.email_contatto = nuova_email
                me.save()
            stato_conferma = True
            del request.session[parametri['session_code']]
            del request.session[parametri['session_key']]
    return stato_conferma, errore_conferma


def termina_deleghe_giovani():
    """
    Termina tutte le deleghe come delegato giovani per quelle persone che non rientrano più nei limiti di età
    """
    meno_di_33 = now().replace(year=now().year - 33)
    deleghe_giovani = Delega.objects.filter(tipo=DELEGATO_OBIETTIVO_5)
    delegati_giovani = deleghe_giovani.values_list('persona', flat=True)
    delegati_giovani_terminare = Persona.objects.filter(data_nascita__lte=meno_di_33, pk__in=delegati_giovani)
    terminare = deleghe_giovani.filter(persona__in=delegati_giovani_terminare)
    for delega in terminare:
        delega.termina(data=mezzanotte_24_ieri(now()))


def random_password(length=12):
    """
    Genera una nuova password con caratteri alfanumerici minuscoli e maiuscoli
    :param length: lunghezza della stringa generata come password
    :return: stringa
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
