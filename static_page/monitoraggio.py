import requests

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

# Typeform API settings
ENDPOINT = "https://api.typeform.com/forms/%s"
TYPEFORM_TOKEN = settings.DEBUG_CONF.get('typeform', 'token')
HEADERS = {
    'Authorization': "Bearer %s" % TYPEFORM_TOKEN,
    'Content-Type': 'application/json'
}


def make_request(form_id, path='', **kwargs):
    url = ENDPOINT % form_id + path
    if kwargs.get('completed') == True:
        url += '?completed=true'
    return requests.get(url, headers=HEADERS)


def get_responses(form_id):
    return make_request(form_id, path='/responses')


def get_completed_responses(form_id):
    response = make_request(form_id, path='/responses', completed=True)
    return response


def get_json_from_responses(form_id=None, instance=None):
    if instance:
        return instance.json()
    else:
        if form_id is not None:
            # Make complete request
            return get_responses(form_id).json()
        else:
            raise BaseException('You must pass form_id')


def get_questions(form_id):
    return make_request(form_id)


class TypeFormResponses:
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

    def __init__(self, request):
        self.request = request

    def has_answers(self, json):
        try:
            items = json['items'][0]
            has_answers = 'answers' in items and len(items['answers']) > 0
        except IndexError:
            # print('items IndexError Exception')
            return False
        else:
            return has_answers  # must return True

    def get_answers_for_json(self, json):
        items = json['items'][0]
        answers = items['answers']
        return answers

    def handle_answer_by_type(self, type, answer):
        if type == 'boolean':
            return 'Si' if answer == True else 'No'
        elif type == 'choices':
            return ', '.join(answer['labels'])

        return answer

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

    def get_form_questions(self, form_id):
        return self.make_request(form_id).json()

    def make_request(self, form_id, path='', **kwargs):
        url = ENDPOINT % form_id + path
        if kwargs.get('completed') == True:
            url += '?completed=true'
        return requests.get(url, headers=HEADERS)

    def get_completed_responses(self, form_id):
        response = self.make_request(form_id, path='/responses', completed=True)
        return response

    def _retrieve_data(self):
        retrieved = dict()
        for form_id, form_name in self.form_ids.items():
            responses_for_form_id = self.get_completed_responses(form_id).json()

            if self.has_answers(responses_for_form_id):
                answers = self.get_answers_for_json(responses_for_form_id)
                answer = answers[0]['field']

                questions = self.get_form_questions(form_id)
                questions_fields = questions['fields']

                for question in questions_fields:
                    if question['ref'] == answer['ref']:
                        combined = self.combine_question_with_user_answer(
                                question=question,
                                answer=answers[0],
                                form_name=form_name
                        )
                        if combined is not None:
                            retrieved[form_id] = combined

        return retrieved

    def get_data(self):
        return self._retrieve_data()

    def render_to_string(self, to_print=False):
        return render_to_string('monitoraggio_print.html', {
            'request': self.request,
            'results': self.get_data(),
            'to_print': to_print,
        })

    def print(self):
        return HttpResponse(self.render_to_string(to_print=True))

    def send_via_mail(self):
        response = self.render_to_string()
        return response
