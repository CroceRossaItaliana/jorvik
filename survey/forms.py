from datetime import datetime, timedelta
from django import forms
from django.forms import ModelForm

from .models import Survey, Question # SurveyResult


class QuestionarioForm(forms.Form):
    CHOICES_1_10 = [(i, i) for i in range(1, 11)]

    step = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.invalid_survey_forms = False

        for f in ['me', 'course', 'instance', 'step']:
            setattr(self, f, kwargs.pop(f))
        super().__init__(*args, **kwargs)


class QuestionarioPaginaIniziale(QuestionarioForm):
    # def process(self, result, next_step):
    #     super().process(result, next_step)
    pass


class SelectDirettoreCorsoForm(QuestionarioForm):
    direttore = forms.CharField(label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        survey, course, step = self.instance, self.course, self.step

        direttori = course.direttori_corso()
        direttori_choices = [(i.pk, i.nome_completo) for i in direttori]
        self.fields['direttore'].widget = forms.RadioSelect(choices=direttori_choices)

    def validate_questionario(self, result, **kwargs):
        form = self
        if form.is_valid():
            cd = form.cleaned_data
            direttore = cd['direttore']

            # Nel caso di direttori multipli ogni direttore ha una sua key (persona.pk)
            if direttore not in result.response_json['direttori']:
                result.response_json['direttori'][direttore] = {}

            # (success): da salvare nella view
            return True

        # Non da salvare
        return False


class ValutazioneDirettoreCorsoForm(QuestionarioForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        survey, course, step = self.instance, self.course, self.step

        self.fields['step'].initial = self.step

        for question in survey.get_questions().filter(question_group__id=1):
            if not question.is_active:
                # skip inactive questions
                continue

            qid = question.qid
            self.fields[qid] = forms.CharField(label=question.text)

            if question.question_type == Question.RADIO:
                self.fields[qid].widget = forms.RadioSelect(choices=self.CHOICES_1_10)
            elif question.question_type == Question.TEXT:
                pass

    # def clean(self):
    #     print(self.cleaned_data)

    def validate_questionario(self, result, **kwargs):
        direttore = kwargs.pop('direttore_da_valutare')

        form = self
        if form.is_valid():
            cd = form.cleaned_data

            risposte_valutazione_direttore = {k.replace('qid_', ''): v for k,v in cd.items() if k.startswith('qid_')}
            result.response_json['direttori'][str(direttore.pk)] = risposte_valutazione_direttore
            result.save()

            return True

        return False


class ValutazioneUtilitaLezioniForm(QuestionarioForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        survey, course = self.instance, self.course
        lezioni = course.get_lezioni_precaricate()

        # print(lezioni)

        for lezione in lezioni:
            lezione_pk = lezione.pk

            self.fields[lezione_pk] = forms.CharField(label=lezione.nome)
            self.fields[lezione_pk].widget = forms.RadioSelect(choices=self.CHOICES_1_10)


class ValutazioneDocenteCorsoForm(QuestionarioForm):
    pass


class RespondToCourseSurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = ['text']

    def __init__(self, *args, **kwargs):
        self.me = kwargs.pop('me')
        self.course = kwargs.pop('course')
        super().__init__(*args, **kwargs)
        self.fields.pop('text')

        # survey = self.instance
        # responses = survey.get_responses_dict(self.me)
        # for question in survey.get_questions():
        #     if not question.is_active:
        #         # skip inactive questions
        #         continue
        #
        #     qid = question.qid
        #     self.fields[qid] = forms.CharField(label=question.text)
        #     field = self.fields[qid]
        #
        #     if qid in responses:
        #         # Set input values if user has already voted
        #         response_for_question = responses[qid]
        #         field.initial = response_for_question['response']
        #
        #         # Disable editing after N time passed since user voted
        #         delta = datetime.now() - response_for_question['object'].created_at
        #         if delta >= timedelta(days=2):
        #             field.widget.attrs["disabled"] = "disabled"
        #
        #     if survey.is_course_admin(self.me, self.course):
        #         # Director of course can see questions but cannot vote
        #         field.widget.attrs["disabled"] = "disabled"
        #
        #     if question.required:
        #         field.required = True
        #         field.widget.attrs["class"] = "required"
        #     else:
        #         field.required = False
