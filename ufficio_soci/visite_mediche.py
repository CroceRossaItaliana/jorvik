from datetime import datetime
from collections import namedtuple
from autenticazione.funzioni import pagina_privata
from anagrafica.permessi.costanti import (GESTIONE_SOCI)
from anagrafica.models import Appartenenza, Persona
from ufficio_soci.api_visitemediche import VisiteMedicheApi

from .forms import DottoriVisitaMedica, PrenotaVisitaMedica, RicercaVisitaMedica, SelezionaComitato


Examination = namedtuple('examination', [
    'doctor', 'patient', 'examination_type', 'examination_status',
    'examination_start', 'examination_end', 'exUuid', 'data'])
Doctor = namedtuple('doctor', ['id', 'uuid', 'name', 'surname', 'officeAddress'])

def formatDate(strDate):
    if strDate:
        try:
            return datetime.strptime(
                strDate, "%Y-%m-%dT%H:%M:%S.%f%z")
        except:
            return None

@pagina_privata
def ricerca_visite_mediche(request, me):
    """ Ricerca visite mediche """

    api = VisiteMedicheApi()
    examination_types = {}
    for t in api.examination_types:
        examination_types[t['etId']] = t['etDescription']
    
    examination_status = {}
    for t in api.examination_status:
        examination_status[t['esId']] = t['description']

    sedi = me.oggetti_permesso(GESTIONE_SOCI)
    stato_visita = []
    stato_visita.extend([
        (stato['esId'], stato['description'])
        for stato in api.examination_status
    ])
    form = RicercaVisitaMedica(
        request.POST or None, comitato=sedi, stato_visita=stato_visita
    )

    items = []

    numpage = request.POST.get('page', 0)
    comitato = request.POST.get('comitato', None)
    exUuid = request.POST.get('exUuid', None)
    stato_visita = request.POST.get('stato_visita', None)

    contesto = {
        'form': form,
        'prenotazione_rimossa': None,
        'comitato': comitato,
        'stato_visita': stato_visita,
    }

    if (comitato and exUuid):
        status = api.remove_examination(examinationID=exUuid)
        contesto['prenotazione_rimossa'] = status == 200

    if request.POST and form.is_valid():
        comitato = form.cleaned_data['comitato']
        stato_visita = form.cleaned_data['stato_visita']
        data_visita = form.cleaned_data['data_visita']

        data = api.search_examination(
            comitato.id,
            statusId=stato_visita,
            date=data_visita and data_visita.strftime("%Y-%m-%d") or None,
            numpage=numpage,
        )
        
        if data and 'content' in data:
            contesto['totalPages'] = data['totalPages']
            contesto['has_previous'] = data['number'] > 0
            contesto['previous_page_number'] = data['number'] - 1
            contesto['next_page_number'] = data['number'] + 1
            contesto['has_next'] = data['totalPages'] > data['number'] + 1
            contesto['number'] = data['number'] + 1
            
            for item in data['content']:
                doctor = api.get_examination_doctor(item['exDoctorUuid'])
                items.append(
                    Examination(
                        doctor=Doctor(
                            uuid=item.get('uuid'),
                            id=item.get('id'),
                            name=doctor.get('name'),
                            surname=doctor.get('surname'),
                            officeAddress=doctor.get('officeAddress'),
                        ),
                        patient=Persona.objects.get(pk=item['exIdPatientExt']),
                        examination_type=examination_types.get(item['exExaminationTypeId'], ''),
                        examination_status=examination_status.get(item['exStatusId'], ''),
                        examination_start=formatDate(item['exStartAt']),
                        examination_end=formatDate(item['exEndAt']),
                        exUuid=item.get('exUuid'),
                        data=item.get('data'),
                    )
                )

    contesto['items'] = items

    return 'us_ricerca_visita_medica.html', contesto


@pagina_privata
def visite_mediche(request, me):
    """ Visite mediche """

    api = VisiteMedicheApi()
    examination_types = {}
    for t in api.examination_types:
        examination_types[t['etId']] = t['etDescription']
    
    examination_status = {}
    for t in api.examination_status:
        examination_status[t['esId']] = t['description']

    items = []

    numpage = request.POST.get('page', 0)
    
    
    data = api.patient_examination(
        patientId=me.pk,
        numpage=numpage,
    )
    
    contesto = {}

    if data and 'content' in data:
        contesto['totalPages'] = data['totalPages']
        contesto['has_previous'] = data['number'] > 0
        contesto['previous_page_number'] = data['number'] - 1
        contesto['next_page_number'] = data['number'] + 1
        contesto['has_next'] = data['totalPages'] > data['number'] + 1
        contesto['number'] = data['number'] + 1
        
        for item in data['content']:
            doctor = api.get_examination_doctor(item['exDoctorUuid'])
            items.append(
                Examination(
                    doctor=Doctor(
                        uuid=item.get('uuid'),
                        id=item.get('id'),
                        name=doctor.get('name'),
                        surname=doctor.get('surname'),
                        officeAddress=doctor.get('officeAddress'),
                    ),
                    patient=Persona.objects.get(pk=item['exIdPatientExt']),
                    examination_type=examination_types.get(item['exExaminationTypeId'], ''),
                    examination_status=examination_status.get(item['exStatusId'], ''),
                    examination_start=formatDate(item['exStartAt']),
                    examination_end=formatDate(item['exEndAt']),
                    exUuid=item.get('exUuid'),
                    data=item.get('data'),
                )
            )

    contesto['items'] = items

    return 'us_visite_mediche.html', contesto


@pagina_privata
def lista_dottori(request, me):
    api = VisiteMedicheApi()
    sedi = me.oggetti_permesso(GESTIONE_SOCI)

    form = DottoriVisitaMedica(
        request.POST or None, comitato=sedi
    )
    
    contesto = {
        'form': form,
        'dottore_associato': None,
        'dottore_rimosso': None,
    }

    numpage = request.POST.get('page', 0)
    numpage_associati = request.POST.get('page_associati', 0)

    comitato = request.POST.get('comitato')
    associa_dottore = request.POST.get('associa_dottore')
    rimuovi_dottore = request.POST.get('rimuovi_dottore')

    if (comitato and associa_dottore):
        status = api.associate_doctor_committee(
            committeeId=comitato, doctorUuid=associa_dottore
        )
        contesto['dottore_associato'] = status == 200
    
    if (rimuovi_dottore):
        status = api.deassociate_doctor_committee(
            rimuovi_dottore
        )

        contesto['dottore_rimosso'] = status == 200

    medici_associabili = []
    medici_associati = []

    if request.POST and form.is_valid():
        comitato = form.cleaned_data['comitato']

        data = api.doctors_list(numpage=numpage, committeeId=comitato.id)

        if data and 'content' in data:
            contesto['totalPages'] = data['totalPages']
            contesto['has_previous'] = data['number'] > 0
            contesto['previous_page_number'] = data['number'] - 1
            contesto['next_page_number'] = data['number'] + 1
            contesto['has_next'] = data['totalPages'] > data['number'] + 1
            contesto['number'] = data['number'] + 1

            for item in data['content']:
                medici_associabili.append(
                    Doctor(
                        uuid=item.get('uuid'),
                        id=item.get('id'),
                        name=item.get('name'),
                        surname=item.get('surname'),
                        officeAddress=item.get('officeAddress'),
                    ),
                )

        data = api.committee_doctors_list(committeeId=comitato.id,
                                numpage=numpage_associati)
       
        if data and 'content' in data:
            contesto['comitato'] = comitato
            contesto['totalPages_associati'] = data['totalPages']
            contesto['has_previous_associati'] = data['number'] > 0
            contesto['previous_page_number_associati'] = data['number'] - 1
            contesto['next_page_number_associati'] = data['number'] + 1
            contesto['has_next_associati'] = data['totalPages'] > data['number'] + 1
            contesto['number_associati'] = data['number'] + 1

            for item in data['content']:
                medici_associati.append(
                    Doctor(
                        uuid=item['doctor'].get('uuid'),
                        id=item.get('dcId'),
                        name=item['doctor'].get('name'),
                        surname=item['doctor'].get('surname'),
                        officeAddress=item['doctor'].get('officeAddress'),
                    ),
                )

    contesto['medici_associabili'] = medici_associabili
    contesto['medici_associati'] = medici_associati

    return 'us_associa_medico.html', contesto


@pagina_privata
def prenota_visita(request, me):
    api = VisiteMedicheApi()
    sedi = me.oggetti_permesso(GESTIONE_SOCI)

    examination_types = {}
    for t in api.examination_types:
        examination_types[t['etId']] = t['etDescription']

    tipi_visita = []
    tipi_visita.extend([
        (tipo['etId'], tipo['etDescription'])
        for tipo in api.examination_types
    ])

    form_comitato = SelezionaComitato(
        request.POST or None, comitato=sedi
    )

    contesto = {
        'form_comitato': form_comitato,
        'esito_prenotazione': None,
    }

    numpage = request.POST.get('page', 0)
    medici_associati = []

    if request.POST and form_comitato.is_valid():
        comitato = form_comitato.cleaned_data['comitato']
        contesto['comitato'] = comitato

        data = api.committee_doctors_list(
            committeeId=comitato.id, numpage=numpage)

        if data and 'content' in data:
            for item in data['content']:
                medici_associati.append((
                    item['doctor'].get('uuid'),
                    "{} {} - {}".format(
                        item['doctor'].get('surname'),
                        item['doctor'].get('name'),
                        item['doctor'].get('officeAddress')
                    )
                ))
    
    if request.POST.get('prenota') != None:
        form_prenotazione = PrenotaVisitaMedica(request.POST, tipo_visita=tipi_visita, dottori=medici_associati,)
        if request.POST and form_prenotazione.is_valid():
            comitato = request.POST.get('comitato')
            paziente = request.POST.get('paziente')
            dottore = request.POST.get('dottore')
            data_visita = datetime.strptime(request.POST.get(
                'data_visita'), '%d/%m/%Y %H:%M').strftime('%Y-%m-%dT%H:%M')
            tipo_visita = request.POST.get('tipo_visita')
            
            status = api.add_examination(
                comitato, dottore, paziente, tipo_visita, data_visita)
            contesto['esito_prenotazione'] = status == 200
            if status == 200:
                form_prenotazione = PrenotaVisitaMedica(
                    tipo_visita=tipi_visita, dottori=medici_associati,)

    else:
        form_prenotazione = PrenotaVisitaMedica(tipo_visita=tipi_visita, dottori=medici_associati,)

    contesto['form_prenotazione'] = form_prenotazione

    return 'us_prenota_visita.html', contesto
