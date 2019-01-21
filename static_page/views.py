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

    TYPEFORM_API_DOMAIN = 'https://api.typeform.com'
    HEADERS = {
        'Authorization': "Bearer 14J1sNRF197fk89WAwzwBfpkLKmDAgjU6r9CTKwoQjim",
        'Content-Type': 'application/json'
    }

    context = {'type_form': dict()}
    user_comitato = me.sede_riferimento().id

    for bottone_name, _id in btns.items():
        endpoint = "%s/forms/%s/responses" % (TYPEFORM_API_DOMAIN, _id)
        r = requests.get(endpoint, headers=HEADERS)
        js = r.json()

        for item in js['items']:
            c = item.get('hidden', dict())
            c = c.get('c')

            if c and c == str(user_comitato):
                context['type_form'][_id] = [False, user_comitato, bottone_name]
                break  # bottone spento
            else:
                context['type_form'][_id] = [True, user_comitato, bottone_name]
                break

    return 'monitoraggio.html', context
