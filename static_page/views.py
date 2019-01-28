from django.shortcuts import render, redirect, get_object_or_404
from autenticazione.funzioni import pagina_privata
from .models import Page


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
    import requests
    from random import randint
    from django.conf import settings

    btns = {
        'Sezione A – servizi di carattere sociale': 'by6gIZ',
        'Sezione B – telefonia sociale, telesoccorso,  teleassistenza e telemedicina': 'AX0Rjm',
        'Sezione C – salute': 'FZlCpn',
        'Sezione D – ''''"ambiente", "sviluppo economico e coesione sociale", 
            "cultura, sport e ricreazione", "cooperazione e solidarietà internazionale",
            "protezione civile"
        "''': "artG8g",
        'Sezione E – relazioni': 'r3IRy8',
        'Sezione F – organizzazione': 'DhH3Mk',
        'Sezione G – risorse economiche e finanziarie': 'W6G6cD',
    }

    if not hasattr(me, 'sede_riferimento'):
        return redirect('/')

    # Django
    context = {'type_form': dict()}
    user_comitato = me.sede_riferimento().id

    # Typeform API
    TYPEFORM_TOKEN = settings.DEBUG_CONF.get('typeform', 'token')
    HEADERS = {
        'Authorization': "Bearer %s" % TYPEFORM_TOKEN,
        'Content-Type': 'application/json'
    }
    endpoint = "https://api.typeform.com/forms/%s/responses"
    btn_values = btns.values()
    test_request = requests.get(
        endpoint % list(btn_values)[randint(0, len(btn_values))],
        headers=HEADERS
    )

    if test_request.status_code != 200:
        return 'monitoraggio.html', context

    for bottone_name, _id in btns.items():
        r = requests.get(endpoint % _id, headers=HEADERS)
        js = r.json()

        type_form_dict = context['type_form']

        for item in js['items']:
            c = item.get('hidden', dict())
            c = c.get('c')

            if c and c == str(user_comitato):
                type_form_dict[_id] = [False, user_comitato, bottone_name]
                break  # bottone spento

        if not _id in type_form_dict:
            type_form_dict[_id] = [True, user_comitato, bottone_name]

    return 'monitoraggio.html', context
