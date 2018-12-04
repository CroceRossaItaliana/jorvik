from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from autenticazione.funzioni import pagina_privata

from anagrafica.permessi.costanti import ERRORE_PERMESSI, MODIFICA
from formazione.models import CorsoBase
from .models import Question, Survey, SurveyResult
from .forms import RespondToCourseSurveyForm


@pagina_privata
def course_survey(request, me, pk):
    course = get_object_or_404(CorsoBase, pk=pk)
    course_info_page_redirect = redirect(reverse('aspirante:info', args=[pk]))

    try:
        survey = Survey.objects.get(corsobase=course)
    except Survey.DoesNotExist:
        messages.error(request, "Il corso non ha un questionario impostato. Contattare l'amministrazione.")
        return course_info_page_redirect

    if not course.concluso:
        messages.error(request, "Il corso non è ancora terminato (non è superata la data di esame)")
        return course_info_page_redirect

    if not survey.can_vote(me, course):
        return redirect(ERRORE_PERMESSI)

    form = RespondToCourseSurveyForm(request.POST or None, instance=survey,
                                     me=me, course=course)
    if form.is_valid():
        cd = form.cleaned_data
        for question in survey.get_questions():
            if question.qid in cd:
                response = cd.get(question.qid)
                result, created = SurveyResult.objects.get_or_create(
                    course=course,
                    user=me,
                    survey=survey,
                    question=question
                )
                if result:
                    result.response = response
                if created:
                    result.can_edit = False
                result.save()

        messages.success(request, 'Grazie, abbiamo salvato le tue risposte.')
        return redirect(reverse('survey:course', args=[course.pk]))

    context = {
        'corso': course,
        'survey': survey,
        'form': form,
        'puo_modificare': survey.is_course_admin(me, course),
        'has_responses': survey.has_user_responses(course),
    }
    return 'corso_questionario_di_gradimento.html', context


@pagina_privata
def course_survey_download_results(request, me, pk):
    course = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(course, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    report = SurveyResult.generate_report_for_course(course)
    return report