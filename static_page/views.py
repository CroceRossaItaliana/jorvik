from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.messages import get_messages

from autenticazione.funzioni import pagina_privata
from anagrafica.permessi.applicazioni import COMMISSARIO, PRESIDENTE
from .models import Page
from .monitoraggio import TypeFormResponses, TypeFormNonSonoUnBersaglio, NONSONOUNBERSAGLIO, MONITORAGGIO ,MONITORAGGIOTYPE


@pagina_privata
def view_page(request, me, slug):
    context = {
        'page': get_object_or_404(Page, slug=slug),
    }
    if slug in ['portale-convenzioni', 'report-violence']:
        context['has_privacy_popup'] = True

    return 'page_view.html', context


@pagina_privata
def monitoraggio(request, me):
    if True not in [me.is_comissario, me.is_presidente]: return redirect('/')
    if not hasattr(me, 'sede_riferimento'): return redirect('/')

    request_comitato = request.GET.get('comitato')
    if me.is_comissario and not request_comitato:
        # GAIA-58: Seleziona comitato
        if me.is_presidente:
            deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])
        else:
            deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO])

        return 'monitoraggio_choose_comitato.html', {
            'deleghe': deleghe.distinct('oggetto_id'),
            'url': 'monitoraggio',
            'titolo': 'Monitoraggio 2019 (dati 2018)',
            'target': MONITORAGGIO
        }

    # Comitato selezionato, mostrare le form di typeform
    context = dict()
    typeform = TypeFormResponses(request=request, me=me)

    # Make test request (API/connection availability, etc)
    if not typeform.make_test_request_to_api:
        return 'monitoraggio.html', context

    context['type_form'] = typeform.context_typeform

    typeform.get_responses_for_all_forms()  # checks for already compiled forms

    is_done = False
    typeform_id = request.GET.get('id', False)
    if typeform_id:
        typeform_ctx = context['type_form'][typeform_id]
        is_done = typeform_ctx[0]
        context['section'] = typeform_ctx
        context['typeform_id'] = typeform_id

    if is_done:
        context['is_done'] = True

    context['comitato'] = typeform.comitato
    context['user_comitato'] = typeform.comitato_id
    context['user_id'] = typeform.get_user_pk
    context['all_forms_are_completed'] = typeform.all_forms_are_completed
    context['target'] = MONITORAGGIO
    # # Get celery_task_id
    # # TODO: ajax polling task is ready
    # prefix = typeform.CELERY_TASK_PREFIX
    # message_storage = get_messages(request)
    # if len(message_storage) > 0:
    #     for line, msg in enumerate(message_storage):
    #         if msg.message.startswith(prefix):
    #             context['celery_task_id'] = msg.message.replace(prefix, '').strip()
    #             del message_storage._loaded_messages[line]

    return 'monitoraggio.html', context


@pagina_privata
def monitoraggio_actions(request, me):
    action = request.GET.get('action')
    target = request.GET.get('target')
    redirect_url = redirect(reverse(MONITORAGGIOTYPE[target][1]))

    if not action: return redirect_url
    if not hasattr(me, 'sede_riferimento'): return redirect_url
    if True not in [me.is_comissario, me.is_presidente]: return redirect('/')

    responses = MONITORAGGIOTYPE[target][0](request=request, me=me)
    if action == 'print':
        return responses.print(redirect_url)
    elif action == 'send_via_mail':
        return responses.send_via_mail(redirect_url, target)


@pagina_privata
def monitoraggio_nonsonounbersaglio(request, me):
    if True not in [me.is_comissario, me.is_presidente]: return redirect('/')
    if not hasattr(me, 'sede_riferimento'): return redirect('/')

    typeform = TypeFormNonSonoUnBersaglio(request=request, me=me)

    request_comitato = request.GET.get('comitato')
    if me.is_comissario and not request_comitato:
        if me.is_presidente:
            deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])
        else:
            deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO])

        return 'monitoraggio_choose_comitato.html', {
            'deleghe': deleghe.distinct('oggetto_id'),
            'url': 'monitoraggio-nonsonounbersaglio',
            'titolo': 'Monitoraggio Non Sono Un Bersaglio',
            'idtypeform': '&id={}'.format(typeform.get_first_typeform()),
            'target': NONSONOUNBERSAGLIO
        }

    context = dict()

    if not typeform.make_test_request_to_api:
        return 'monitoraggio_nonsonounbersaglio.html', context

    context['type_form'] = typeform.context_typeform

    typeform.get_responses_for_all_forms()

    is_done = False
    typeform_id = request.GET.get('id', False)
    if typeform_id:
        typeform_ctx = context['type_form'][typeform_id]
        is_done = typeform_ctx[0]
        context['typeform_id'] = typeform_id

    if is_done:
        context['is_done'] = True

    context['comitato'] = typeform.comitato
    context['idtypeform'] = '&id={}'.format(typeform.get_first_typeform())
    context['user_comitato'] = typeform.comitato_id
    context['user_id'] = typeform.get_user_pk
    context['all_forms_are_completed'] = typeform.all_forms_are_completed
    context['target'] = NONSONOUNBERSAGLIO

    return 'monitoraggio_nonsonounbersaglio.html', context
