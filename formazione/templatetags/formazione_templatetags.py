from django import template
from django.utils.safestring import mark_safe

from base.utils import oggi


register = template.Library()

@register.simple_tag
def titoli_del_corso(persona, cd):
    init_query = persona.titoli_personali_confermati().filter(is_course_title=True)
    lista = init_query.filter(titolo__in=cd['titoli'])

    if cd.get('show_only_active', False):
        lista = lista.filter(data_scadenza__gte=oggi())

    return {
        'lista': lista.order_by('-data_scadenza'),
        'num_of_titles': init_query.count()
    }


@register.simple_tag
def lezione_esonero(lezione, partecipante):
    from ..models import AssenzaCorsoBase

    kwargs = {
        'lezione': lezione,
        'persona': partecipante,
    }

    a = None

    try:
        a = AssenzaCorsoBase.objects.get(**kwargs)

    except AssenzaCorsoBase.DoesNotExist:
        return None
    except AssenzaCorsoBase.MultipleObjectsReturned:
        a = AssenzaCorsoBase.objects.filter(**kwargs).last()

    if a:
        return a if a.is_esonero else None
    return None


@register.simple_tag
def lezione_partecipante_pk_shortcut(lezione, partecipante):
    return "%s-%s" % (lezione.pk, partecipante.pk)


@register.simple_tag
def corsi_filter():
    from ..models import Corso

    href = """<a href="?stato=%s">%s</a>"""
    return mark_safe(' '.join([href % (i[0], i[1]) for i in Corso.STATO]))


@register.simple_tag(takes_context=True)
def can_show_button_genera_verbale(context, corso):
    request = context['request']
    num_verbale_da_generare = 2 if 'seconda_data_esame' in request.GET else 1

    if corso.relazione_direttore.is_completed:
        if num_verbale_da_generare == 1:
            return True
        elif num_verbale_da_generare == 2:
            if not corso.has_partecipazioni_confermate_con_assente_motivo:
                return True
    return False


@register.simple_tag(takes_context=True)
def can_show_tab_questionario(context):
    corso, me = context['corso'], context['me']
    if corso.survey and corso.concluso:  # corso.is_nuovo_corso
        return corso.survey.can_vote(me, corso)
    return False


@register.simple_tag
def generate_area_id_selector(area_nome):
    area_id = area_nome.lower().replace(' ', "_")
    return area_id


@register.simple_tag
def attestato_titolo(corso):
    from curriculum.models import Titolo

    if corso.tipo == corso.BASE:
        return " di qualifica volontario CRI"
    else:
        if corso.cdf_level in [Titolo.CDF_LIVELLO_I]:
            return " di partecipazione"
        else:
            return " di qualifica"
    return ''


@register.simple_tag
def attestato_obiettivi_formativi(corso):
    text = corso.titolo_cri.scheda_obiettivi
    if not text:
        return ''

    phrases = ['Nello specifico il corso mira', 'Nello specifico, il corso mira']
    for phrase in phrases:
        if phrase.lower() in text.lower():
            new_text = text[:text.find(phrase)]
            return new_text.strip()
    return text


@register.simple_tag
def attestato_contenuti(corso):
    if corso.titolo_cri:
        if corso.titolo_cri.scheda_lezioni:
            return [i['lezione'] for i in corso.titolo_cri.scheda_lezioni_sorted.values()]
    return list()


@register.simple_tag
def attestato_replace_corso_name(titolo):
    titolo_lc = titolo.lower()
    if titolo_lc.startswith("corso informativo"):
        return titolo

    for i in ['Corso per', 'Corso di']:
        if titolo_lc.startswith(i.lower()):
            return titolo.replace(i, '').strip().capitalize()

    return titolo
