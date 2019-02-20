from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.core.urlresolvers import reverse
from autenticazione.funzioni import pagina_privata
from .models import Page
from .monitoraggio import (get_responses, get_json_from_responses, TypeFormResponses)


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
    if not hasattr(me, 'sede_riferimento'):
        return redirect('/')

    btns = TypeFormResponses.form_ids

    # Django
    user_comitato = me.sede_riferimento().id
    context = {
        'type_form': {k: [False, user_comitato, v] for k, v in btns.items()}
    }

    # Test request
    if get_responses(list(btns.keys())[0]).status_code != 200:
        return 'monitoraggio.html', context

    for _id, bottone_name in btns.items():
        json = get_json_from_responses(_id)
        for item in json['items']:
            c = item.get('hidden', dict())
            c = c.get('c')

            if c and c == str(user_comitato):
                context['type_form'][_id][0] = True
                break  # bottone spento

    is_done = False
    typeform_id = request.GET.get('id', False)
    if typeform_id:
        typeform = context['type_form'][typeform_id]
        is_done = typeform[0]
        context['section'] = typeform
        context['typeform_id'] = typeform_id

    if is_done:
        context['is_done'] = True
    else:
        context['user_comitato'] = user_comitato
        context['user_id'] = request.user.id

    context['all_forms_are_completed'] = False if False in [v[0] for k,v in context['type_form'].items()] else True

    return 'monitoraggio.html', context


@pagina_privata
def monitoraggio_actions(request, me):
    redirect_url = redirect(reverse('pages:monitoraggio'))
    if not hasattr(me, 'sede_riferimento'):
        return redirect_url

    action = request.GET.get('action')
    if not action:
        return redirect_url

    responses = TypeFormResponses(request)

    if action == 'print':
        return responses.print()
    elif action == 'send_via_mail':
        return responses.send_via_mail()
