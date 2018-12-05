from datetime import datetime, timedelta
from django import forms
from django.forms import ModelForm

from .models import Survey


class RespondToCourseSurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = ['text']

    def __init__(self, *args, **kwargs):
        self.me = kwargs.pop('me')
        self.course = kwargs.pop('course')
        super().__init__(*args, **kwargs)
        self.fields.pop('text')

        survey = self.instance
        responses = survey.get_responses_dict(self.me)
        for question in survey.get_questions():
            if not question.is_active:
                # skip inactive questions
                continue

            qid = question.qid
            self.fields[qid] = forms.CharField(label=question.text)
            field = self.fields[qid]

            if qid in responses:
                # Set input values if user has already voted
                response_for_question = responses[qid]
                field.initial = response_for_question['response']

                # Disable editing after N time passed since user voted
                delta = datetime.now() - response_for_question['object'].created_at
                if delta >= timedelta(days=2):
                    field.widget.attrs["disabled"] = "disabled"

            if survey.is_course_admin(self.me, self.course):
                # Director of course can see questions but cannot vote
                field.widget.attrs["disabled"] = "disabled"

            if question.required:
                field.required = True
                field.widget.attrs["class"] = "required"
            else:
                field.required = False
