import requests
from io import BytesIO
from celery import uuid
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from anagrafica.models import Persona
from static_page.tasks import send_mail


class TypeFormResponses:
    CELERY_TASK_PREFIX = 'CELERY_TASK_MSG_'
    TYPEFORM_DOMAIN = "https://api.typeform.com"
    TYPEFORM_TOKEN = settings.DEBUG_CONF.get('typeform', 'token')
    ENDPOINT = TYPEFORM_DOMAIN + "/forms/%s"
    HEADERS = {
        'Authorization': "Bearer %s" % TYPEFORM_TOKEN,
        'Content-Type': 'application/json'
    }

    form_ids = {
        'by6gIZ': 'Sezione A – servizi di carattere sociale',
        'AX0Rjm': 'Sezione B – telefonia sociale, telesoccorso, teleassistenza e telemedicina',
        'FZlCpn': 'Sezione C – salute',
        'artG8g': 'Sezione D – ''''"ambiente", "sviluppo economico e coesione sociale", 
            "cultura, sport e ricreazione", "cooperazione e solidarietà internazionale",
            "protezione civile"''',
        'r3IRy8': 'Sezione E – relazioni',
        'DhH3Mk': 'Sezione F – organizzazione',
        'W6G6cD': 'Sezione G – risorse economiche e finanziarie',
    }

    def __init__(self, request=None, me=None, user_pk=None):
        self.request = request
        self.me = me
        self.user_pk = user_pk

        self.context_typeform = self._set_typeform_context()

    def _set_typeform_context(self):
        # This method generates a dict values,
        # False as default value means that form_id is not completed yet.
        user_comitato = self.user_comitato
        return {k: [False, user_comitato, v] for k, v in self.form_ids.items()}

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
        if self.user_pk is None:
            return self.me
        else:
            return Persona.objects.get(id=self.get_user_pk)

    @property
    def user_comitato(self):
        persona = self.persona
        return persona.sede_riferimento().id

    def get_responses_for_all_forms(self):
        for _id, bottone_name in self.form_ids.items():
            json = self.get_json_from_responses(_id)
            for item in json['items']:
                c = item.get('hidden', dict())
                c = c.get('c')

                if c and c == str(self.user_comitato):
                    self.context_typeform[_id][0] = True
                    break  # bottone spento

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

    def get_json_from_responses(self, form_id=None, instance=None):
        if instance:
            return instance.json()
        else:
            if form_id is not None:
                # Make complete request
                # return self.get_responses(form_id).json()
                return self.get_completed_responses(form_id).json()
            else:
                raise BaseException('You must pass form_id')

    def get_completed_responses(self, form_id):
        response = self.make_request(form_id,
                                     path='/responses',
                                     query=self.get_user_pk,
                                     completed=True)
        return response

    def get_answers_from_json(self, json):
        items = json['items'][0]
        answers = items['answers']
        return answers

    def get_form_questions(self, form_id):
        return self.make_request(form_id).json()

    def combine_question_with_user_answer(self, **kwargs):
        question = kwargs.get('question')
        answer = kwargs.get('answer')

        type = answer['type']

        if question and answer:
            return {
                'question_id': question['id'],
                'question_ref': question['ref'],
                'question_title': question['title'],
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
            return ', '.join(answer['labels'])
        elif type == 'choice':
            return answer['label']
        elif type == 'number':
            pass

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

    def _retrieve_data(self):
        retrieved = dict()
        for form_id, form_name in self.form_ids.items():
            responses_for_form_id = self.get_completed_responses(form_id).json()

            if self.has_answers(responses_for_form_id):
                answers = self.get_answers_from_json(responses_for_form_id)
                answers_refactored = {i['field']['ref']: i for i in answers}

                questions = self.get_form_questions(form_id)
                questions_fields = questions['fields']

                for question in questions_fields:
                    if question['ref'] in answers_refactored:
                        combined = self.combine_question_with_user_answer(
                                question=question,
                                answer=answers_refactored[question['ref']],
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
            'request': self.request,
            'results': self._retrieve_data(),
            'to_print': to_print,
        })

    def print(self):
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

    def send_via_mail(self):
        task = send_mail.apply_async(args=(self.get_user_pk,), task_id=uuid())

        messages.add_message(self.request, messages.INFO, self.CELERY_TASK_PREFIX+task.id)
        return redirect(reverse('pages:monitoraggio'))