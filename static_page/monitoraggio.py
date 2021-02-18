import requests
from io import BytesIO
from collections import OrderedDict
from celery import uuid
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from anagrafica.models import Persona, Sede
from anagrafica.permessi.applicazioni import COMMISSARIO, PRESIDENTE
from .tasks import send_mail, send_mail_regionale


class TypeForm:
    CELERY_TASK_PREFIX = 'CELERY_TASK_MSG_'
    TYPEFORM_DOMAIN = "https://api.typeform.com"
    TYPEFORM_TOKEN = settings.TOKEN_TYPE_FORM
    ENDPOINT = TYPEFORM_DOMAIN + "/forms/%s"
    HEADERS = {
        'Authorization': "Bearer %s" % TYPEFORM_TOKEN,
        'Content-Type': 'application/json'
    }

    def __init__(self, request=None, me=None, user_pk=None):
        self.request = request
        self.me = me
        self.user_pk = user_pk  # Celery

        self.context_typeform = self._set_typeform_context()

    # python 3.5
    form_ids = OrderedDict([])

    @property
    def get_user_pk(self):
        if self.request is not None:
            return self.request.user.persona.pk
        elif self.me is not None:
            return self.me.pk
        elif self.user_pk is not None:
            return self.user_pk

    @property
    def persona(self):
        if self.me is not None:
            return self.me
        if self.user_pk is not None:
            return Persona.objects.get(id=self.get_user_pk)

    @property
    def comitato_id(self):
        persona = self.persona

        deleghe = persona.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])

        request_comitato = self.request.GET.get('comitato') if self.request else None
        if request_comitato:
            # Check comitato_id validity
            if int(request_comitato) not in deleghe.values_list('oggetto_id', flat=True):
                raise ValueError("L'utenza non ha una delega con l'ID del comitato indicato.")
            return request_comitato
        else:
            if persona.is_presidente:
                # Il ruolo presidente può avere soltanto una delega attiva,
                # quindi vado sicuro a prendere <oggetto_id> dell'unico record
                return deleghe.filter(tipo=PRESIDENTE).last().oggetto_id

    @property
    def comitato(self):
        if self.comitato_id:
            return Sede.objects.get(id=self.comitato_id)
        else:
            return Sede.objects.none()

    @property
    def all_forms_are_completed(self):
        return 0 if False in [v[0] for k, v in self.context_typeform.items()] else 1

    @classmethod
    def make_request(cls, form_id, path='', **kwargs):
        url = cls.ENDPOINT % form_id + path
        if kwargs.get('completed') == True and kwargs.get('query'):
            url += '?completed=true'
            url += '&query=%s' % kwargs.get('query')
        response = requests.get(url, headers=cls.HEADERS)
        return response

    @property
    def make_test_request_to_api(self):
        first_form_id = list(self.form_ids.keys())[0]
        response = self.make_request(form_id=first_form_id, path='/responses')
        return response.status_code == 200

    @property
    def user_details(self):
        if self.request is not None:
            # Not celery
            return self.request.user.persona
        else:
            # Called within celery task
            return self.persona

    def _set_typeform_context(self):
        # This method generates a dict values,
        # False as default value means that form_id is not completed yet.
        return {k: [False, self.comitato_id, v] for k, v in self.form_ids.items()}

    def get_responses_for_all_forms(self):
        comitato_id = str(self.comitato_id)
        for _id, bottone_name in self.form_ids.items():
            json = self.get_json_from_responses(_id)
            print(json)
            for item in json['items']:
                c = item.get('hidden', OrderedDict())
                c = c.get('c')

                if c and c == comitato_id:
                    self.context_typeform[_id][0] = True
                    break  # bottone spento

    def get_json_from_responses(self, form_id=None, instance=None):
        if instance:
            return instance.json()
        else:
            if form_id is not None:
                # Make complete request
                # return self.get_responses(form_id).json()
                return self.get_completed_responses(form_id)
            else:
                raise BaseException('You must pass form_id')

    def get_completed_responses(self, form_id):
        response = self.make_request(form_id,
                                     path='/responses',
                                     query=self.get_user_pk,
                                     completed=True)
        return response.json()

    def get_answers_from_json(self, json):
        items = json['items'][0]
        answers = items['answers']
        return answers

    def get_form_questions(self, form_id):
        response = self.make_request(form_id)
        return response.json()

    def combine_question_with_user_answer(self, **kwargs):
        question = kwargs.get('question')
        answer = kwargs.get('answer')
        answer = answer[0] if len(answer) > 0 else None

        type = answer['type']

        if question and answer:
            return {
                'question_id': question['id'],
                # 'question_ref': question['ref'],
                'question_title': question['title'],
                'question_parent': question['parent'] if 'parent' in question else dict(),
                'answer_field_id': answer['field']['id'],
                'answer_field_type': answer['field']['type'],
                'answer_field_ref': answer['field']['ref'],
                'answer_type': type,
                'answer': self.handle_answer_by_type(type, answer[type]),
                'form_name': kwargs.get('form_name'),
            }
        else:
            return None

    def handle_answer_by_type(self, type, answer):
        if type == 'boolean':
            return 'Si' if answer == True else 'No'
        elif type == 'choices':
            if 'labels' in answer:
                return ', '.join(answer['labels'])
            elif 'other' in answer:
                return answer.get('other')
        elif type == 'choice':
            return answer.get('label') or answer.get('other')
        elif type in ['text', 'number', 'email', 'url', 'file_url', 'date', 'payment']:
            return answer

    def has_answers(self, json):
        try:
            items = json['items'][0]
            has_answers = 'answers' in items and len(items['answers']) > 0
        except IndexError:
            # print('items IndexError Exception')
            return False
        else:
            return has_answers  # must return True

    def collect_questions(self, form_id):
        # requested url:  https://api.typeform.com/forms/<form_id>

        questions = self.get_form_questions(form_id)
        questions_without_hierarchy = OrderedDict()

        # eh si, lo so è un bella camminata...
        for field in questions['fields']:
            if 'properties' in field:
                if 'fields' in field['properties']:
                    question_parent = {i: field[i] for i in ['id', 'title']}

                    questions_without_hierarchy[field['ref']] = {i: field[i] for i in ['id', 'title']}

                    for i in field['properties']['fields']:
                        questions_without_hierarchy[i['ref']] = {_: i[_] for _ in ['id', 'title']}

                        if question_parent:
                            questions_without_hierarchy[i['ref']]['parent'] = question_parent
                            # reset variable, to avoid displaying data in each table row (show only 1 time)
                            question_parent = OrderedDict()

                        if 'properties' in i:
                            for k, v in i['properties'].items():
                                if 'choices' in k:
                                    labels = [label for label in v]
                                    questions_without_hierarchy[i['ref']]['labels'] = labels
                else:
                    questions_without_hierarchy[field['ref']] = {i: field[i] for i in ['id', 'title']}
            else:
                questions_without_hierarchy[field['ref']] = {i: field[i] for i in ['id', 'title']}

        return questions_without_hierarchy

    def _retrieve_data(self):
        retrieved = OrderedDict()
        for form_id, form_name in self.form_ids.items():
            responses_for_form_id = self.get_completed_responses(form_id)

            if self.has_answers(responses_for_form_id):
                answers = self.get_answers_from_json(responses_for_form_id)
                answers_refactored = OrderedDict([(i['field']['ref'], [i]) for i in answers])

                questions_fields = self.collect_questions(form_id)
                for answer_ref, answer_data in answers_refactored.items():
                    if answer_ref in questions_fields.keys():
                        question = questions_fields[answer_ref]
                        combined = self.combine_question_with_user_answer(
                                question=question,
                                answer=answer_data,
                                form_name=form_name
                        )

                        if form_id not in retrieved:
                            retrieved[form_id] = [combined]
                        else:
                            retrieved[form_id].append(combined)

        if not retrieved:
            self._no_data_retrieved = True

        return retrieved

    def _render_to_string(self, to_print=False):
        return render_to_string('monitoraggio_print.html', {
            'user_details': self.user_details,
            'request': self.request,
            'results': self._retrieve_data(),
            'to_print': to_print,
        })

    def print(self, redirect_url):
        html = self._render_to_string(to_print=True)

        if hasattr(self, '_no_data_retrieved'):
            messages.add_message(self.request, messages.ERROR,
                                 'Non ci sono i dati per generare il report.')
            return redirect(reverse('pages:monitoraggio'))

        return HttpResponse(html)

    def convert_html_to_pdf(self):
        html = self._render_to_string().encode('utf-8')
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html), result, encoding='UTF-8')
        if not pdf.err:
            return result.getvalue()

    def download_as_pdf(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=file.pdf'
        response.write(self.convert_html_to_pdf())
        return response

    def send_via_mail(self, redirect_url, target):
        task = send_mail.apply_async(args=(self.get_user_pk, target), task_id=uuid())

        # messages.add_message(self.request, messages.INFO, self.CELERY_TASK_PREFIX+task.id)
        return redirect_url

    def send_via_mail_regionale(self, redirect_url, target):
        task = send_mail_regionale.apply_async(args=(self.get_user_pk, target), task_id=uuid())

        # messages.add_message(self.request, messages.INFO, self.CELERY_TASK_PREFIX+task.id)
        return redirect_url


class TypeFormResponses(TypeForm):
    form_ids = OrderedDict([
        ('ttOyXCJR', 'A-GOVERNANCE'),
        ('PZvVJIZq', 'B-Personale Dipendente e Volontario'),
        ('p5DlUCLt', 'C-Contabilità'),
        ('o7JfxbE5', 'D-Convenzioni e progetti'),
        ('ZwMX5rsG', 'E-Relazioni esterne, comunicazione, trasparenza'),
    ])
    email_body = """Grazie per aver completato il Questionario autocontrollo."""

    email_body_regionale = """
        Gentilissimi, \n
        in allegato la Checklist di autovalutazione del Comitato {}
    """

    email_object = 'Risposte Questionario di autocontrollo di %s'


class TypeFormNonSonoUnBersaglio(TypeForm):
    form_ids = OrderedDict([
        ('KLyNcY', 'HCID'),
    ])

    email_body = '''Grazie per aver completato il Monitoraggio Campagna NON SONO UN BERSAGLIO.\n
    Nell'apprezzare la collaborazione prestata, vi confermiamo la corretta ricezione del modulo compilato.\n'''

    email_object = 'Risposte monitoraggio NON SONO UN BERSAGLIO%s'


    def get_first_typeform(self):
        return list(self.form_ids.items())[0][0]


class TypeFormResponsesTrasparenza(TypeForm):
    form_ids = OrderedDict([
        ('Jo7AmkVU', 'Questionatio Trasparenza L. 124/2017'),
    ])
    email_body = """Grazie per aver completato il Questionario sulla trasparenza."""

    # REGIONALE
    email_body_regionale = """
        Gentilissimi, \n
        in allegato la Checklist di autovalutazione del Comitato {}
    """

    email_object = 'Risposte Questionario trasparenza di %s'
    @property
    def comitato_id(self):
        persona = self.persona

        delegato = persona.delega_responsabile_area_trasparenza

        if delegato:
            return delegato.oggetto.sede.pk

        deleghe = persona.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])

        request_comitato = self.request.GET.get('comitato') if self.request else None
        if request_comitato:
            # Check comitato_id validity
            if int(request_comitato) not in deleghe.values_list('oggetto_id', flat=True):
                raise ValueError("L'utenza non ha una delega con l'ID del comitato indicato.")
            return request_comitato
        else:
            if persona.is_presidente:
                # Il ruolo presidente può avere soltanto una delega attiva,
                # quindi vado sicuro a prendere <oggetto_id> dell'unico record
                return deleghe.filter(tipo=PRESIDENTE).last().oggetto_id




MONITORAGGIO = 'monitoraggio'
NONSONOUNBERSAGLIO = 'nonsonounbersaglio'
MONITORAGGIO_TRASPARENZA = 'monitoraggiotrasparenza'


MONITORAGGIOTYPE = {
    MONITORAGGIO: (TypeFormResponses, 'pages:monitoraggio'),
    MONITORAGGIO_TRASPARENZA: (TypeFormResponsesTrasparenza, 'pages:monitoraggio-trasparenza'),
    NONSONOUNBERSAGLIO: (TypeFormNonSonoUnBersaglio, 'pages:monitoraggio-nonsonounbersaglio')
}


class TypeFormResponsesTrasparenzaCheck:

    CELERY_TASK_PREFIX = 'CELERY_TASK_MSG_'
    TYPEFORM_DOMAIN = "https://api.typeform.com"
    TYPEFORM_TOKEN = settings.TOKEN_TYPE_FORM
    ENDPOINT = TYPEFORM_DOMAIN + "/forms/%s"
    HEADERS = {
        'Authorization': "Bearer %s" % TYPEFORM_TOKEN,
        'Content-Type': 'application/json'
    }

    form_ids = OrderedDict([
        ('Jo7AmkVU', 'Questionario Trasparenza L. 124/2017')
    ])

    def __init__(self, persona=None, user_pk=None, comitato_id=None):
        # self.request = request
        self.me = persona
        self.comitato_id = comitato_id
        self.user_pk = user_pk  # Celery

        self.context_typeform = self._set_typeform_context()

    def _set_typeform_context(self):
        # This method generates a dict values,
        # False as default value means that form_id is not completed yet.
        print()
        return {k: [False, self.comitato_id, v] for k, v in self.form_ids.items()}

    def get_responses_for_all_forms(self):
        comitato_id = str(self.comitato_id)
        for _id, bottone_name in self.form_ids.items():
            json = self.get_json_from_responses(_id)
            for item in json['items']:
                c = item.get('hidden', OrderedDict())
                c = c.get('c')

                if c and c == comitato_id:
                    self.context_typeform[_id][0] = True
                    break  # bottone spento

    def get_json_from_responses(self, form_id=None, instance=None):
        if instance:
            return instance.json()
        else:
            if form_id is not None:
                # Make complete request
                # return self.get_responses(form_id).json()
                return self.get_completed_responses(form_id)
            else:
                raise BaseException('You must pass form_id')

    def get_completed_responses(self, form_id):
        response = self.make_request(form_id,
                                     path='/responses',
                                     query=self.user_pk,
                                     completed=True)
        return response.json()

    @classmethod
    def make_request(cls, form_id, path='', **kwargs):
        url = cls.ENDPOINT % form_id + path
        if kwargs.get('completed') == True and kwargs.get('query'):
            url += '?completed=true'
            url += '&query=%s' % kwargs.get('query')
        response = requests.get(url, headers=cls.HEADERS)
        return response

    @property
    def all_forms_are_completed(self):
        return 0 if False in [v[0] for k, v in self.context_typeform.items()] else 1

    def _render_to_string(self, to_print=False):
        return render_to_string('monitoraggio_print.html', {
            'user_details': self.me,
            # 'request': self.request,
            'results': self._retrieve_data(),
            'to_print': to_print,
        })

    def has_answers(self, json):
        try:
            items = json['items'][0]
            has_answers = 'answers' in items and len(items['answers']) > 0
        except IndexError:
            # print('items IndexError Exception')
            return False
        else:
            return has_answers  # must return True

    def get_answers_from_json(self, json):
        items = json['items'][0]
        answers = items['answers']
        return answers

    def _retrieve_data(self):
        retrieved = OrderedDict()
        for form_id, form_name in self.form_ids.items():
            responses_for_form_id = self.get_completed_responses(form_id)

            if self.has_answers(responses_for_form_id):
                answers = self.get_answers_from_json(responses_for_form_id)
                answers_refactored = OrderedDict([(i['field']['ref'], [i]) for i in answers])

                questions_fields = self.collect_questions(form_id)
                for answer_ref, answer_data in answers_refactored.items():
                    if answer_ref in questions_fields.keys():
                        question = questions_fields[answer_ref]
                        combined = self.combine_question_with_user_answer(
                                question=question,
                                answer=answer_data,
                                form_name=form_name
                        )

                        if form_id not in retrieved:
                            retrieved[form_id] = [combined]
                        else:
                            retrieved[form_id].append(combined)

        if not retrieved:
            self._no_data_retrieved = True

        return retrieved

    def collect_questions(self, form_id):
        # requested url:  https://api.typeform.com/forms/<form_id>

        questions = self.get_form_questions(form_id)
        questions_without_hierarchy = OrderedDict()

        # eh si, lo so è un bella camminata...
        for field in questions['fields']:
            if 'properties' in field:
                if 'fields' in field['properties']:
                    question_parent = {i: field[i] for i in ['id', 'title']}

                    questions_without_hierarchy[field['ref']] = {i: field[i] for i in ['id', 'title']}

                    for i in field['properties']['fields']:
                        questions_without_hierarchy[i['ref']] = {_: i[_] for _ in ['id', 'title']}

                        if question_parent:
                            questions_without_hierarchy[i['ref']]['parent'] = question_parent
                            # reset variable, to avoid displaying data in each table row (show only 1 time)
                            question_parent = OrderedDict()

                        if 'properties' in i:
                            for k, v in i['properties'].items():
                                if 'choices' in k:
                                    labels = [label for label in v]
                                    questions_without_hierarchy[i['ref']]['labels'] = labels
                else:
                    questions_without_hierarchy[field['ref']] = {i: field[i] for i in ['id', 'title']}
            else:
                questions_without_hierarchy[field['ref']] = {i: field[i] for i in ['id', 'title']}

        return questions_without_hierarchy

    def combine_question_with_user_answer(self, **kwargs):
        question = kwargs.get('question')
        answer = kwargs.get('answer')
        answer = answer[0] if len(answer) > 0 else None

        type = answer['type']

        if question and answer:
            return {
                'question_id': question['id'],
                # 'question_ref': question['ref'],
                'question_title': question['title'],
                'question_parent': question['parent'] if 'parent' in question else dict(),
                'answer_field_id': answer['field']['id'],
                'answer_field_type': answer['field']['type'],
                'answer_field_ref': answer['field']['ref'],
                'answer_type': type,
                'answer': self.handle_answer_by_type(type, answer[type]),
                'form_name': kwargs.get('form_name'),
            }
        else:
            return None

    def get_form_questions(self, form_id):
        response = self.make_request(form_id)
        return response.json()

    def handle_answer_by_type(self, type, answer):
        if type == 'boolean':
            return 'Si' if answer == True else 'No'
        elif type == 'choices':
            if 'labels' in answer:
                return ', '.join(answer['labels'])
            elif 'other' in answer:
                return answer.get('other')
        elif type == 'choice':
            return answer.get('label') or answer.get('other')
        elif type in ['text', 'number', 'email', 'url', 'file_url', 'date', 'payment']:
            return answer

    def print(self):
        html = self._render_to_string(to_print=True)

        # if hasattr(self, '_no_data_retrieved'):
        #     messages.add_message(self.request, messages.ERROR,
        #                          'Non ci sono i dati per generare il report.')
        #     return redirect(reverse('pages:monitoraggio'))

        return HttpResponse(html)
