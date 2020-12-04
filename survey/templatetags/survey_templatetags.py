from django import template
from django.utils.safestring import mark_safe

from anagrafica.models import Persona
from formazione.models import LezioneCorsoBase
from ..models import Question


register = template.Library()

@register.simple_tag
def add_questions_groups_to_survey_form(form, survey):
    from lxml import etree

    html_output = ''
    added_groups = list()
    questions = survey.question_set.all()

    for f in form.split('</div>'):
        div_formgroup = f + "</div>"
        html = etree.HTML(div_formgroup)
        if html is not None:
            input_xpath = html.xpath('//div[@class="form-group"]//input/@name')
            question_id = input_xpath[0].replace('qid_', '')
            question_group = questions.get(id=question_id).question_group

            if question_group not in added_groups:
                added_groups.append(question_group)
                html_output += '<div class="survey__group-name">%s</div>' % question_group

        html_output += div_formgroup

    return mark_safe(html_output)


@register.simple_tag
def questionario_pdf_utilita_lezioni(utilita_lezioni_dict):
    if not utilita_lezioni_dict:
        return dict()

    lezioni_not_existing = list()
    for lezione_pk in utilita_lezioni_dict.keys():
        if not LezioneCorsoBase.objects.filter(pk=lezione_pk).count():
            lezioni_not_existing.append(lezione_pk)

    return {
        LezioneCorsoBase.objects.get(pk=k).nome: v for k, v in utilita_lezioni_dict.items()
        if k not in lezioni_not_existing
    }


@register.simple_tag
def questionario_pdf_direttori(direttori_dict):
    if not direttori_dict:
        return dict()

    return {
        Persona.objects.get(pk=direttore_pk).nome_completo:
            {
                Question.objects.get(pk=domanda_pk).text: risposta
                for domanda_pk, risposta in voti.items()
            }
        for direttore_pk, voti in direttori_dict.items()
    }


@register.simple_tag
def questionario_pdf_valutazione_lezioni(lezioni_dict):
    lezioni_dict_new = dict()
    for docente_pk, lezioni in lezioni_dict.items():
        if docente_pk.isalpha() or '_' in docente_pk:
            p = docente_pk
        else:
            p = Persona.objects.get(pk=docente_pk).nome_completo

        if p not in lezioni_dict_new:
            lezioni_dict_new[p] = dict()

        lezioni_not_existing = list()  # to avoid RuntimeError dictionary size changed
        lezioni_dict_new[p] = lezioni

        for lezione_pk in lezioni.keys():
            if not LezioneCorsoBase.objects.filter(pk=lezione_pk).count():
                lezioni_not_existing.append(lezione_pk)

        lezioni_dict_new[p] = {
            LezioneCorsoBase.objects.get(pk=lezione_pk): {
                Question.objects.get(pk=domanda_pk): voto for domanda_pk, voto in v.items() if domanda_pk != 'completed'
            }
            for lezione_pk, v in lezioni.items() if lezione_pk not in lezioni_not_existing
        }

    return lezioni_dict_new
