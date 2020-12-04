from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from autenticazione.funzioni import pagina_privata
from anagrafica.permessi.costanti import ERRORE_PERMESSI, MODIFICA
from anagrafica.models import Persona
from formazione.models import CorsoBase, LezioneCorsoBase
from .models import Survey, SurveyResult


@pagina_privata
def course_survey(request, me, pk):
    redir_to_course = redirect(reverse('aspirante:info', args=[pk]))

    course = get_object_or_404(CorsoBase, pk=pk)

    if not course.concluso:
        messages.error(request, "Il corso non è ancora terminato (non è superata la data di esame)")
        return redir_to_course

    try:
        survey = Survey.objects.get(corsobase=course)
    except Survey.DoesNotExist:
        # Se il corso non ha agganciato un questionario
        messages.error(request, "Il corso non ha un questionario impostato. Contattare l'amministrazione.")
        return redir_to_course

    if not survey.can_vote(me, course):
        return redirect(ERRORE_PERMESSI)

    if survey.is_course_admin(me, course):
        if me.pk not in course.partecipazioni_confermate().values_list('persona__pk', flat=True):
            messages.error(request, 'Direttori e amministratori del corso non possono compilare il questionario.')
            return redir_to_course

    survey_url = reverse("survey:course", args=[pk,])

    context = {
        'corso': course,
        'survey': survey,
        'puo_modificare': survey.is_course_admin(me, course),
        'has_responses': survey.has_user_responses(course),
        'forms': list(),
    }

    # Scegli le form sulla base di step indicato in http-request
    step_in_request = request.POST.get('step') or request.GET.get('step')
    step_in_dict = SurveyResult.STEPS.get(step_in_request, [None, None, None])
    step, form, next_step = step_in_dict

    # Crea/trova oggetto per le risposte
    try:
        result, created = SurveyResult.objects.get_or_create(course=course,
                                                             user=me,
                                                             survey=survey)
        result.new_version = True
        result.save()

    except SurveyResult.MultipleObjectsReturned:
        if SurveyResult.get_responses_for_course(course).filter(new_version=False).exists():
            messages.error(request, "Il questionario è stato già compilato.")
            return redir_to_course

    if result.concluso and step != 6:
        messages.success(request, "Grazie per la compilazione di tutto il questionario.")
        return redir_to_course

    context['survey_result'] = result

    # Valorizza il campo json senza dati (keys vuoti)
    if result and not result.response_json:
        result.response_json = {
            'direttori': dict(),
            'utilita_lezioni': dict(),
            'lezioni': dict(),
            'step': None,
        }
        result.save()

    if step_in_request:
        form_kwargs = dict(instance=survey,
                           course=course,
                           step=step_in_request,
                           survey_result=result,
                           me=me)
        if step:
            context['step'] = step

        if form:
            # Instanziare form per step
            form = form(request.POST or None, **form_kwargs)
            context['form'] = form

    # Variabili
    direttore_persona = None
    invalid_forms = False

    continue_step = result.response_json['step']
    if continue_step:
        context['continue_step'] = survey_url + "?step=%s" % continue_step

        direttore_selezionato = list(result.response_json['direttori'].keys())
        if direttore_selezionato:
            if len(direttore_selezionato):
                direttore_persona = Persona.objects.get(pk=int(direttore_selezionato[0]))
            else:
                direttore_persona = Persona.objects.filter(pk__in=[int(i) for i in direttore_selezionato])

    # Steo (0): Inizio
    if request.GET.get('from') and request.GET.get('from') == 'start':
        result.response_json['step'] = SurveyResult.SELEZIONA_DIRETTORE
        result.save()

    # Argomenti
    kwargs_per_questionario = dict()
    if step_in_request == SurveyResult.VALUTAZIONE_DIRETTORE:
        kwargs_per_questionario['direttore_da_valutare'] = direttore_persona

    elif step_in_request == SurveyResult.VALUTAZIONE_DOCENTE:
        docente, lezione = result.get_uncompleted_valutazione_docente_lezione()
        if docente and lezione:
            if isinstance(docente, int):
                context['valutazione_docente'] = Persona.objects.get(pk=docente)
            else:
                context['valutazione_docente'] = docente.replace('de_', '')

            context['valutazione_lezione'] = LezioneCorsoBase.objects.get(pk=lezione)
        else:
            result.response_json['step'] = next_step
            result.save()

            messages.warning(request, "Non ci sono docenti da valutare o "
                                      "questo step è stato già completato.")
            return redirect(survey_url)

    # Arriva form da validare e salvare
    if (request.method == 'POST') and (form is not None):
        """ Possibili steps:
            (1): Seleziona direttore
            (2): Valutazione direttore
            (3): Valutazione lezioni
            (4): Valutazione di ogni docente di ogni lezione
            (5): Valutazione organizzazione e servizi
            (6): Grazie.
        """

        # Valida form collegaga allo step attuale
        # Importante restituire [True o False]
        is_questionario_valid = form.validate_questionario(result, **kwargs_per_questionario)
        if not is_questionario_valid:
            # Segna che ci sono form invalide per non procede al salvataggio
            invalid_forms = True

        # Non ci sono form invalide. La form è tutta compilata.
        # Imposta prossimo step -> Salva risultato - > Rindirizza pagina prox.step
        if not invalid_forms:
            # Valutazione docente -> lezione
            # Prossimo step rimane sempre lo stesso finchè non sono state
            # compilate tutte le combinazioni docente\lezione.
            if step == 4 and result.get_uncompleted_valutazione_docente_lezione()[0] is not None:
                return redirect(survey_url + "?step=%s" % SurveyResult.VALUTAZIONE_DOCENTE)

            result.response_json['step'] = next_step
            result.save()

            # Rindirizza
            next_step_qs = "?step=%s" % next_step if next_step is not None else ''
            next_step_reverse = survey_url + next_step_qs

            return redirect(next_step_reverse)

    context['template'] = 'survey_step_%s_inc.html' % step
    return 'corso_questionario_di_gradimento.html', context


@pagina_privata
def course_survey_download_results(request, me, pk):
    course = get_object_or_404(CorsoBase, pk=pk)
    if not me.permessi_almeno(course, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    report = SurveyResult.get_report_for_course(course, request)
    return report
