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

from anagrafica.models import Persona, Sede
from anagrafica.permessi.applicazioni import COMMISSARIO, PRESIDENTE
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

    # python 3.5
    form_ids = OrderedDict([
        ('by6gIZ', 'Sezione A – servizi di carattere sociale'),
        ('AX0Rjm',
         'Sezione B – telefonia sociale, telesoccorso, teleassistenza e telemedicina'),
        ('FZlCpn', 'Sezione C – salute'),
        ('artG8g', 'Sezione D – ''''"ambiente", "sviluppo economico e coesione sociale",
                "cultura, sport e ricreazione", "cooperazione e solidarietà internazionale",
                "protezione civile"'''),
        ('r3IRy8', 'Sezione E – relazioni'),
        ('DhH3Mk', 'Sezione F – organizzazione'),
        ('W6G6cD', 'Sezione G – risorse economiche e finanziarie')
    ])

    def __init__(self, request=None, me=None, user_pk=None):
        self.request = request
        self.me = me
        self.user_pk = user_pk

        self.context_typeform = self._set_typeform_context()

    def _set_typeform_context(self):
        # This method generates a dict values,
        # False as default value means that form_id is not completed yet.
        return {k: [False, self.comitato_id, v] for k, v in self.form_ids.items()}

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
    def comitato_id(self):
        deleghe = self.me.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])

        request_comitato = self.request.GET.get('comitato')
        if request_comitato:
            # Check comitato_id validity
            if int(request_comitato) not in deleghe.values_list('oggetto_id', flat=True):
                raise ValueError("L'utenza non ha una delega con l'ID del comitato indicato.")
            return request_comitato
        else:
            if self.me.is_presidente:
                # Il ruolo presidente può avere soltanto una delega attiva,
                # quindi vado sicuro a prendere <oggetto_id> dell'unico record
                return deleghe.filter(tipo=PRESIDENTE).last().oggetto_id

    @property
    def comitato(self):
        if self.comitato_id:
            return Sede.objects.get(id=self.comitato_id)
        else:
            return Sede.objects.none()

    def get_responses_for_all_forms(self):
        comitato_id = str(self.comitato_id)
        for _id, bottone_name in self.form_ids.items():
            json = self.get_json_from_responses(_id)
            for item in json['items']:
                c = item.get('hidden', dict())
                c = c.get('c')

                if c and c == comitato_id:
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
                # 'question_ref': question['ref'],
                'question_title': question['title'],
                'question_parent': question['parent'] if 'parent' in question else {},
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

    def collect_questions(self, form_id):
        # requested url:  https://api.typeform.com/forms/<form_id>

        questions = self.get_form_questions(form_id)
        questions_without_hierarchy = dict()

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
                            question_parent = {}

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
        retrieved = dict()
        for form_id, form_name in self.form_ids.items():
            responses_for_form_id = self.get_completed_responses(form_id).json()

            if self.has_answers(responses_for_form_id):
                answers = self.get_answers_from_json(responses_for_form_id)
                answers_refactored = {i['field']['ref']: i for i in answers}

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
