# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.utils.timezone import now

from anagrafica.models import Persona, Delega
from anagrafica.permessi.applicazioni import DELEGATO_OBIETTIVO_5
from base.utils import mezzanotte_24_ieri
from curriculum.models import Titolo
from jorvik.settings import ELASTIC_HOST, ELASTIC_QUICKPROFILE_INDEX, STATIC_PROD_BASEURL
from posta.models import Messaggio
from ufficio_soci.models import Tesserino


def quick_profile_feeding(pp):
    url = "{}/{}/_doc/".format(ELASTIC_HOST, ELASTIC_QUICKPROFILE_INDEX)

    headers = {
        'Content-Type': 'application/json'
    }
    aspirante = True if hasattr(pp, 'aspirante') else False

    payload = {'_id': pp.id, 'nome': pp.nome, 'cognome': pp.cognome, 'sospeso': pp.sospeso,
               'codice_fiscale': pp.codice_fiscale, 'data_nascita': str(pp.data_nascita),
               'dipendente': pp.dipendente, 'volontario': pp.volontario, 'aspirante': aspirante,
               'avatar': STATIC_PROD_BASEURL + pp.avatar.url if pp.avatar else None, 'donatore': {}}

    if hasattr(pp, 'donatore'):
        payload['donatore'] = dict(gruppo_sanguigno=pp.donatore.gruppo_sanguigno,
                                   fattore_rh=pp.donatore.fattore_rh,
                                   fenotipo_rh=pp.donatore.fenotipo_rh)

    payload['tesserino'] = []
    try:
        tesserini = pp.tesserini.filter(valido=True)  #Tesserino.objects.filter(valido=True, persona=pp.id)
        for tesserino in tesserini:
            _tesserino = dict(codice=tesserino.codice, data_scadenza=str(tesserino.data_scadenza),
                              comitato=tesserino.emesso_da.nome, comitato_indirizzo=str(tesserino.emesso_da.locazione))
            payload['tesserino'].append(_tesserino)

    except ObjectDoesNotExist as e:
        payload['tesserino'] = []

    _patenti = []

    for _ in pp.titoli_personali.filter(titolo__tipo=Titolo.PATENTE_CIVILE):
        _patenti.append(dict(tipo=str(_.titolo), # dict(Titolo.TIPO)[Titolo.PATENTE_CIVILE],
                             data_ottenimento=str(_.data_ottenimento), data_scadenza=str(_.data_scadenza) if _.data_scadenza else ''))

    _titoli_cri = []
    for _ in pp.titoli_personali.filter(titolo__tipo=Titolo.TITOLO_CRI):
        _titoli_cri.append(dict(tipo=str(_.titolo), # dict(Titolo.TIPO)[Titolo.TITOLO_CRI],
                                data_ottenimento=str(_.data_ottenimento), data_scadenza=str(_.data_scadenza) if _.data_scadenza else ''))

    _altri_titoli = []
    for _ in pp.titoli_personali.filter(titolo__tipo=Titolo.ALTRI_TITOLI):
        _altri_titoli.append(dict(tipo=str(_.titolo), # dict(Titolo.TIPO)[Titolo.ALTRI_TITOLI],
                                  data_ottenimento=str(_.data_ottenimento), data_scadenza=str(_.data_scadenza) if _.data_scadenza else ''))

    payload['patenti'] = _patenti
    payload['titoli_cri'] = _titoli_cri
    payload['altri_titoli'] = _altri_titoli

    _id = payload.pop('_id')
    response = requests.request("POST", url + str(_id), headers=headers, json=payload, verify=False)
    print(response.text)


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
