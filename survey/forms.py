from django import forms
from django.forms import ModelForm

from .models import Survey, SurveyResult, Question


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
                continue

            qid = question.qid
            self.fields[qid] = forms.CharField(label=question.text)

            if qid in responses:
                # Set input values if user has already voted
                response_for_question = responses[qid]
                self.fields[qid].initial = response_for_question['response']

            if survey.is_course_admin(self.me, self.course):
                # Director of course can see but cannot vote
                self.fields[qid].widget.attrs["disabled"] = "disabled"

            if question.required:
                self.fields[qid].required = True
                self.fields[qid].widget.attrs["class"] = "required"
            else:
                self.fields[qid].required = False
