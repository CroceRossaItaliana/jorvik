from collections import OrderedDict
from datetime import date, datetime

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.clickjacking import xframe_options_exempt

from anagrafica.costanti import REGIONALE, LOCALE, PROVINCIALE
from anagrafica.models import Sede, Persona
from autenticazione.funzioni import pagina_privata, pagina_pubblica
from anagrafica.permessi.applicazioni import COMMISSARIO, PRESIDENTE, RESPONSABILE_FORMAZIONE, DELEGATO_AREA
from jorvik.settings import REACT_UI_BASE_URL
from .models import Page, TypeFormCompilati
from .monitoraggio import TypeFormResponses, TypeFormNonSonoUnBersaglio, NONSONOUNBERSAGLIO, MONITORAGGIO, \
    MONITORAGGIOTYPE, MONITORAGGIO_TRASPARENZA, TypeFormResponsesTrasparenza, TypeFormResponsesTrasparenzaCheck, \
    TypeFormResponsesAutocontrolloCheck, TypeFormResponsesFabbisogniFormativiTerritoriale, \
    MONITORAGGIO_FABBISOGNI_FORMATIVI_TERRITORIALE, MONITORAGGIO_FABBISOGNI_FORMATIVI_REGIONALE, \
    TypeFormResponsesFabbisogniFormativiRegionali, TypeFormResponsesFabbisogniFormativiTerritorialeCheck, \
    TypeFormResponsesFabbisogniFormativiRagionaleCheck, TypeFormResponsesAutocontrolloCheck, \
    TypeFormResponsesTrasparenzaCheckPubblica
from datetime import datetime
from anagrafica.costanti import area_roma_capitale_pk, area_roma_capitale_coordinamento_pk


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
    if True not in [me.is_comissario, me.is_presidente, me.is_delega_responsabile_area_trasparenza]: return redirect('/')
    if not hasattr(me, 'sede_riferimento'): return redirect('/')

    request_comitato = request.GET.get('comitato')
    if (me.is_comissario or me.is_presidente or me.is_delega_responsabile_area_trasparenza) and not request_comitato:
        # GAIA-58: Seleziona comitato
        if me.is_presidente:
            deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])
        elif me.is_comissario:
            deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO])
        else:
            deleghe = [Sede.objects.get(pk=area.oggetto.sede.pk) for area in me.delege_responsabile_area_trasparenza]

        return 'monitoraggio_choose_comitato.html', {
            'deleghe': deleghe.distinct('oggetto_id') if me.is_comissario else deleghe,
            'url': 'monitoraggio',
            'titolo': 'Questionario autocontrollo',
            'target': MONITORAGGIO
        }

    # Comitato selezionato, mostrare le form di typeform
    context = dict()
    context['user_comitato'] = request_comitato
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

    delegha_list = []
    deleghe = [a for a in me.deleghe_attuali().filter(tipo__in=[PRESIDENTE, COMMISSARIO, DELEGATO_AREA])]
    for ogni_delegha in deleghe:
        if ogni_delegha.oggetto_id == int(request_comitato):
            delegha_list.append(ogni_delegha)

    if typeform.all_forms_are_completed == 1:
        typeform_in_db = TypeFormCompilati.objects.filter(
            Q(tipo='Monitoragio Autocontollo') &
            Q(comitato__pk=request_comitato))
        if not typeform_in_db:
            TypeFormCompilati.objects.create(
                tipo='Monitoragio Autocontollo',
                comitato=Sede.objects.get(pk=int(request_comitato)),
                persona=me,
                delega=delegha_list[0].get_tipo_display()
            )

    context['comitato'] = typeform.comitato
    context['user_comitato'] = typeform.comitato_id
    context['user_id'] = typeform.get_user_pk
    context['all_forms_are_completed'] = typeform.all_forms_are_completed

    context['target'] = MONITORAGGIO
    # Get celery_task_id
    # TODO: ajax polling task is ready
    # prefix = typeform.CELERY_TASK_PREFIX
    # message_storage = get_messages(request)
    # if len(message_storage) > 0:
    #     for line, msg in enumerate(message_storage):
    #         if msg.message.startswith(prefix):
    #             context['celery_task_id'] = msg.message.replace(prefix, '').strip()
    #             del message_storage._loaded_messages[line]

    return 'monitoraggio.html', context


@pagina_privata
def monitoraggio_trasparenza(request, me):
    if True not in [me.is_comissario, me.is_presidente, me.is_delega_responsabile_area_trasparenza]: return redirect('/')
    if not hasattr(me, 'sede_riferimento'): return redirect('/')

    return 'benemerenze_iframe.html', {
        'titolo': 'Questionario L. 124/2017',
        'url': "{}/sovvenzioni".format(REACT_UI_BASE_URL),
        'token': me.utenza.qr_login_token(120)
    }

    # request_comitato = request.GET.get('comitato')
    # if (me.is_comissario or me.is_presidente or me.is_delega_responsabile_area_trasparenza) and not request_comitato:
    #     # GAIA-58: Seleziona comitato
    #     if me.is_presidente:
    #         deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO, PRESIDENTE])
    #     elif me.is_comissario:
    #         deleghe = me.deleghe_attuali(tipo__in=[COMMISSARIO])
    #     else:
    #         deleghe = [Sede.objects.get(pk=area.oggetto.sede.pk) for area in me.delege_responsabile_area_trasparenza]

    #     return 'monitoraggio_choose_comitato.html', {
    #         'deleghe': deleghe.distinct('oggetto_id') if me.is_comissario else deleghe,
    #         'url': 'monitoraggio-trasparenza',
    #         'titolo': 'Monitoraggio Trasparenza',
    #         'target': MONITORAGGIO_TRASPARENZA
    #     }

    # # Comitato selezionato, mostrare le form di typeform
    # context = dict()
    # typeform = TypeFormResponsesTrasparenza(request=request, me=me)

    # # Make test request (API/connection availability, etc)
    # if not typeform.make_test_request_to_api:
    #     context['can_compile'] = datetime.now() < datetime(2021, 6, 12, 0, 0)
    #     return 'monitoraggio_trasparenza.html', context

    # context['type_form'] = typeform.context_typeform

    # typeform.get_responses_for_all_forms()  # checks for already compiled forms

    # is_done = False
    # typeform_id = request.GET.get('id', False)
    # if typeform_id:
    #     typeform_ctx = context['type_form'][typeform_id]
    #     is_done = typeform_ctx[0]
    #     context['section'] = typeform_ctx
    #     context['typeform_id'] = typeform_id

    # if is_done:
    #     context['is_done'] = True

    # delegha_list = []
    # deleghe = [a for a in me.deleghe_attuali().filter(tipo__in=[PRESIDENTE, COMMISSARIO, DELEGATO_AREA])]
    # for ogni_delegha in deleghe:
    #     if ogni_delegha.oggetto_id == int(request_comitato):
    #         delegha_list.append(ogni_delegha)

    # if typeform.all_forms_are_completed == 1:
    #     typeform_in_db = TypeFormCompilati.objects.filter(
    #         Q(tipo='Questionario Trasparenza L. 124/2017') &
    #         Q(comitato__pk=request_comitato))
    #     if not typeform_in_db:
    #         TypeFormCompilati.objects.create(
    #             tipo='Questionario Trasparenza L. 124/2017',
    #             comitato=Sede.objects.get(pk=int(request_comitato)),
    #             persona=me,
    #             delega=delegha_list[0].get_tipo_display()
    #         )

    # context['can_compile'] = datetime.now() < datetime(2021, 6, 12, 0, 0)
    # context['comitato'] = typeform.comitato
    # context['user_comitato'] = typeform.comitato_id
    # context['user_id'] = typeform.get_user_pk
    # context['nome_comitato'] = context['comitato'].nome_completo
    # context['nome_regionale'] = context['comitato'].sede_regionale.nome_completo
    # context['all_forms_are_completed'] = typeform.all_forms_are_completed

    # context['target'] = MONITORAGGIO_TRASPARENZA

    # return 'monitoraggio_trasparenza.html', context


@pagina_privata
def monitoraggio_fabb_info_territoriale(request, me):
    if True not in [me.is_presidente_o_commissario_territoriale, me.is_responsabile_formazione]: return redirect('/')
    if not hasattr(me, 'sede_riferimento'): return redirect('/')

    request_comitato = request.GET.get('comitato')
    if (me.is_presidente_o_commissario_territoriale or me.is_responsabile_formazione_territoriale) and not request_comitato:
        # GAIA-58: Seleziona comitato
        if me.is_presidente:
            deleghe = me.deleghe_presidente_o_commissario_territoriale
        elif me.is_comissario:
            deleghe = me.deleghe_commissario_territoriale
        else:
            deleghe = me.is_responsabile_formazione_territoriale
        return 'monitoraggio_choose_comitato.html', {
            'deleghe': deleghe,
            # 'deleghe': deleghe.distinct('oggetto_id') if me.is_comissario else deleghe,
            'url': 'monitoraggio-fabb-info-territoriale',
            'titolo': 'Monitoraggio Fabbisogni Informativi Comitato Territoriale',
            'target': MONITORAGGIO_FABBISOGNI_FORMATIVI_TERRITORIALE
        }

    context = dict()
    context['can_compile'] = datetime.now() < datetime(2021, 8, 4, 0, 0)
    typeform = TypeFormResponsesFabbisogniFormativiTerritoriale(request=request, me=me)

    # Make test request (API/connection availability, etc)
    if not typeform.make_test_request_to_api:
        context['user_comitato'] = request_comitato
        return 'monitoraggio_fabb_info_territoriale.html', context

    context['type_form'] = typeform.context_typeform

    typeform.get_responses_for_all_forms()  # checks for already compiled forms

    is_done = False
    finito_di_compilare_per_questo_anno = False
    typeform_id = request.GET.get('id', False)
    if typeform_id:
        typeform_ctx = context['type_form'][typeform_id]
        is_done = typeform_ctx[0]
        context['section'] = typeform_ctx
        context['typeform_id'] = typeform_id
    if is_done:
        context['is_done'] = True

    today = datetime.today()
    questo_anno = datetime.today().year
    trenta_uno_luglio = '{}-07-31'.format(questo_anno)
    if today > datetime.strptime(trenta_uno_luglio, '%Y-%m-%d'):
        finito_di_compilare_per_questo_anno = True

    delegha_list = []
    deleghe = [a for a in me.deleghe_attuali().filter(tipo__in=[PRESIDENTE, COMMISSARIO, RESPONSABILE_FORMAZIONE])]
    for ogni_delegha in deleghe:
        if ogni_delegha.oggetto_id == int(request_comitato):
            delegha_list.append(ogni_delegha)

    if typeform.all_forms_are_completed == 1:
        typeform_in_db = TypeFormCompilati.objects.filter(
            Q(tipo='Questionario Fabbisogni Formativi Territoriali') &
            Q(comitato__pk=request_comitato))
        if not typeform_in_db:
            TypeFormCompilati.objects.create(
                tipo='Questionario Fabbisogni Formativi Territoriali',
                comitato=Sede.objects.get(pk=int(request_comitato)),
                persona=me,
                delega=delegha_list[0].get_tipo_display()
            )

    context['comitato'] = typeform.comitato
    context['user_comitato'] = typeform.comitato_id
    context['user_id'] = typeform.get_user_pk
    context['nome_comitato'] = context['comitato'].nome_completo
    context['nome_regionale'] = context['comitato'].sede_regionale.nome_completo
    context['all_forms_are_completed'] = typeform.all_forms_are_completed
    context['finito_di_compilare_per_questo_anno'] = finito_di_compilare_per_questo_anno
    context['target'] = MONITORAGGIO_FABBISOGNI_FORMATIVI_TERRITORIALE

    return 'monitoraggio_fabb_info_territoriale.html', context


@pagina_privata
def monitoraggio_fabb_info_regionale(request, me):
    if True not in [me.is_presidente_o_commissario_regionale, me.is_responsabile_formazione]: return redirect('/')
    if not hasattr(me, 'sede_riferimento'): return redirect('/')
    request_comitato = request.GET.get('comitato')
    if (me.is_presidente_o_commissario_regionale or me.is_responsabile_formazione_regionale) and not request_comitato:
        # GAIA-58: Seleziona comitato
        if me.is_presidente_regionale:
            deleghe = me.deleghe_presidente_o_commissario_regionale
        elif me.is_commissario_regionale:
            deleghe = me.deleghe_commissario_regionale
        else:
            deleghe = me.is_responsabile_formazione_regionale

        return 'monitoraggio_choose_comitato.html', {
            'deleghe': deleghe,
            # 'deleghe': deleghe.distinct('oggetto_id') if me.is_comissario else deleghe,
            'url': 'monitoraggio-fabb-info-regionale',
            'titolo': 'Monitoraggio Fabbisogni Informativi Comitato Regionale',
            'target': MONITORAGGIO_FABBISOGNI_FORMATIVI_REGIONALE
        }

    # Comitato selezionato, mostrare le form di typeform
    context = dict()
    typeform = TypeFormResponsesFabbisogniFormativiRegionali(request=request, me=me)

    # Make test request (API/connection availability, etc)
    if not typeform.make_test_request_to_api:
        return 'monitoraggio_trasparenza.html', context

    context['type_form'] = typeform.context_typeform

    typeform.get_responses_for_all_forms()  # checks for already compiled forms

    is_done = False
    finito_di_compilare_per_questo_anno = False
    typeform_id = request.GET.get('id', False)
    if typeform_id:
        typeform_ctx = context['type_form'][typeform_id]
        is_done = typeform_ctx[0]
        context['section'] = typeform_ctx
        context['typeform_id'] = typeform_id
    if is_done:
        context['is_done'] = True
    today = datetime.today()
    # print(date.today())
    # data_tjeter = '2021-05-23'
    questo_anno = datetime.today().year
    trenta_setembre = '{}-10-04'.format(questo_anno)
    if today > datetime.strptime(trenta_setembre, '%Y-%m-%d'):
        finito_di_compilare_per_questo_anno = True

    delegha_list = []
    deleghe = [a for a in me.deleghe_attuali().filter(tipo__in=[PRESIDENTE, COMMISSARIO, RESPONSABILE_FORMAZIONE])]
    for ogni_delegha in deleghe:
        if ogni_delegha.oggetto_id == int(request_comitato):
            delegha_list.append(ogni_delegha)
    if typeform.all_forms_are_completed == 1:
        typeform_in_db = TypeFormCompilati.objects.filter(
            Q(tipo='Questionario Fabbisogni Formativi Regionali') &
            Q(comitato__pk=request_comitato))
        if not typeform_in_db:
            TypeFormCompilati.objects.create(
                tipo='Questionario Fabbisogni Formativi Regionali',
                comitato=Sede.objects.get(pk=int(request_comitato)),
                persona=me,
                delega=delegha_list[0].get_tipo_display()
            )

    context['comitato'] = typeform.comitato
    context['user_comitato'] = typeform.comitato_id
    context['user_id'] = typeform.get_user_pk
    context['nome_comitato'] = context['comitato'].nome_completo
    context['nome_regionale'] = context['comitato'].sede_regionale.nome_completo
    context['all_forms_are_completed'] = typeform.all_forms_are_completed
    context['finito_di_compilare_per_questo_anno'] = finito_di_compilare_per_questo_anno

    context['target'] = MONITORAGGIO_FABBISOGNI_FORMATIVI_REGIONALE

    return 'monitoraggio_fabb_info_regionale.html', context


@pagina_privata
def monitoraggio_actions(request, me):
    action = request.GET.get('action')
    target = request.GET.get('target')
    redirect_url = redirect(reverse(MONITORAGGIOTYPE[target][1]))

    if not action: return redirect_url
    if not hasattr(me, 'sede_riferimento'): return redirect_url
    if True not in [me.is_comissario, me.is_presidente, me.is_delega_responsabile_area_trasparenza, me.is_responsabile_formazione]: return redirect('/')

    responses = MONITORAGGIOTYPE[target][0](request=request, me=me)
    responses.get_responses_for_all_forms()
    if action == 'print':
        return responses.print(redirect_url)
    elif action == 'send_via_mail':
        messages.success(request, "e-mail inviata correttamente")
        return responses.send_via_mail(redirect_url, target)
    elif action == 'send_via_mail_regionale':
        messages.success(request, "e-mail inviata correttamente")
        return responses.send_via_mail_regionale(redirect_url, target)


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


@pagina_privata
def monitora_trasparenza(request, me):
    context = {}
    ids_regionale = []
    id_regionale = request.GET.get('r', None)
    action = request.GET.get('action', None)
    comitato = request.GET.get('comitato', None)

    if not id_regionale and not action and not comitato:
        if me.delega_presidente_e_commissario_regionale:
            for obj in me.delega_presidente_e_commissario_regionale:
                ids_regionale.append(obj)
        ids_regionale.extend(me.delgato_regionale_monitoraggio_trasparenza)

    if ids_regionale:
        regionali = Sede.objects.filter(pk__in=ids_regionale)
        return 'monitoraggio_choose_monitoraggio_transparenza.html', {
            'comitati': regionali,
        }

    if action and comitato:
        sede = Sede.objects.get(pk=comitato)
        delegato = sede.delegati_monitoraggio_trasparenza()
        typeform = TypeFormResponsesTrasparenzaCheck(
            persona=delegato, comitato_id=sede.id, users_pk=delegato
        )
        typeform.get_responses_for_all_forms()
        if action == 'print':
            return typeform.print()

    if id_regionale:
        struttura = OrderedDict()
        regionale = Sede.objects.get(pk=id_regionale)
        locali = regionale.ottieni_discendenti(includimi=True).filter(estensione__in=[LOCALE, REGIONALE]).order_by(
            '-estensione')
        for locale in locali:
            typeform_db = TypeFormCompilati.objects.filter(
                Q(tipo__icontains='trasparenza') & Q(comitato__pk=locale.pk)).first()
            if typeform_db:
                struttura[locale] = 1
            else:
                struttura[locale] = 0
        context['struttura'] = struttura
    else:
        context['regionali'] = Sede.objects.filter(estensione=REGIONALE, attiva=True)

    return 'monitora_trasparenza.html', context


@pagina_privata
def monitora_autocontrollo(request, me):
    context = {}
    ids_regionale = []
    id_regionale = request.GET.get('r', None)
    action = request.GET.get('action', None)
    comitato = request.GET.get('comitato', None)

    if not id_regionale and not action and not comitato:
        if me.delega_presidente_e_commissario_regionale:
            for obj in me.delega_presidente_e_commissario_regionale:
                ids_regionale.append(obj)
        ids_regionale.extend(me.delgato_regionale_monitoraggio_trasparenza)

    if ids_regionale:
        regionali = Sede.objects.filter(pk__in=ids_regionale)
        return 'monitoraggio_choose_monitoraggio_autocontrollo.html', {
            'comitati': regionali,
        }

    if action and comitato:
        sede = Sede.objects.get(pk=comitato)
        delegato = sede.delegati_monitoraggio_trasparenza()
        typeform = TypeFormResponsesAutocontrolloCheck(
            persona=delegato, comitato_id=sede.id, users_pk=delegato
        )
        typeform.get_responses_for_all_forms()
        if action == 'print':
            return typeform.print()

    if id_regionale:
        struttura = OrderedDict()
        regionale = Sede.objects.get(pk=id_regionale)
        locali = regionale.ottieni_discendenti(includimi=True).filter(estensione__in=[LOCALE, REGIONALE]).order_by('-estensione')
        for locale in locali:
            # delegato = locale.delegati_monitoraggio_trasparenza()
            # typeform = TypeFormResponsesAutocontrolloCheck(
            #     persona=delegato, comitato_id=locale.id, users_pk=delegato
            # )
            # typeform.get_responses_for_all_forms()
            # struttura[locale] = typeform.all_forms_are_completed
            if locale.pk==area_roma_capitale_coordinamento_pk:
                locale=Sede.objects.get(pk=area_roma_capitale_pk)

            typeform_db = TypeFormCompilati.objects.filter(
                Q(tipo__icontains='auto') & Q(comitato__pk=locale.pk)).first()
            if typeform_db:
                struttura[locale] = 1
            else:
                struttura[locale] = 0

        context['struttura'] = struttura
    else:
        context['regionali'] = Sede.objects.filter(estensione=REGIONALE, attiva=True)
    return 'monitora_autocontrollo.html', context


@pagina_privata
def monitora_fabb_info_territoriale(request, me):
    context = {}
    ids_regionale = []
    id_regionale = request.GET.get('r', None)
    action = request.GET.get('action', None)
    comitato = request.GET.get('comitato', None)

    if not id_regionale and not action and not comitato:
        if me.delega_presidente_e_commissario_regionale or me.delega_responsabile_formazione_regionale:
            for obj in me.delega_presidente_e_commissario_regionale:
                ids_regionale.append(obj)
            for obj in me.delega_responsabile_formazione_regionale:
                ids_regionale.append(obj)
        ids_regionale.extend(me.delgato_ragionale_monitoraggio_fabb_info)

    if ids_regionale:
        regionali = Sede.objects.filter(pk__in=ids_regionale)
        return 'monitoraggio_choose_monitoraggio_fabb_info_territoriale.html', {
            'comitati': regionali,
        }

    if action and comitato:
        sede = Sede.objects.get(pk=comitato)
        delegato = sede.monitora_fabb_info_regionali()
        typeform = TypeFormResponsesFabbisogniFormativiTerritorialeCheck(
            persona=delegato, comitato_id=sede.id, users_pk=delegato
        )
        typeform.get_responses_for_all_forms()
        from .utils import download_comitati_discendenti, download_excel
        if action == 'print':
            return typeform.print()
        elif action == 'download':
            # return typeform.download_excel()
            return download_excel(sede, comitato, request.path)
        else:
            return download_comitati_discendenti(sede, request.path)

    if id_regionale:
        struttura = OrderedDict()
        regionale = Sede.objects.get(pk=id_regionale)
        locali = regionale.ottieni_discendenti(includimi=True).filter(estensione__in=[LOCALE, PROVINCIALE]).order_by('-estensione')
        for locale in locali:
            # delegato = locale.monitora_fabb_info_regionali()
            # typeform = TypeFormResponsesFabbisogniFormativiTerritorialeCheck(
            #     persona=delegato, comitato_id=locale.id, users_pk=delegato
            # )
            # typeform.get_responses_for_all_forms()
            # struttura[locale] = typeform.all_forms_are_completed
            typeform_db = TypeFormCompilati.objects.filter(
                Q(tipo__icontains='Territoriali') & Q(comitato__pk=locale.pk)).first()
            if typeform_db:
                struttura[locale] = 1
            else:
                struttura[locale] = 0
        # context['struttura'] = struttura
        context['struttura'] = struttura
        context['comitato_regionale'] = id_regionale
    else:
        context['regionali'] = Sede.objects.filter(estensione=REGIONALE, attiva=True)
    return 'monitora_fabb_info_territoriale.html', context


@pagina_privata
def monitora_fabb_info_regionale(request, me):
    context = {}
    ids_regionale = []
    id_regionale = request.GET.get('r', None)
    action = request.GET.get('action', None)
    comitato = request.GET.get('comitato', None)

    if not id_regionale and not action and not comitato:
        if me.delega_presidente_e_commissario_regionale:
            for obj in me.delega_presidente_e_commissario_regionale:
                ids_regionale.append(obj)
        ids_regionale.extend(me.delgato_ragionale_monitoraggio_fabb_info)

    if ids_regionale:
        regionali = Sede.objects.filter(pk__in=ids_regionale)
        return 'monitoraggio_choose_monitoraggio_fabb_info_regionale.html', {
            'comitati': regionali,
        }

    if action and comitato:
        sede = Sede.objects.get(pk=comitato)
        delegato = sede.monitora_fabb_info_regionali()
        typeform = TypeFormResponsesFabbisogniFormativiRagionaleCheck(
            persona=delegato, comitato_id=sede.id, users_pk=delegato
        )
        typeform.get_responses_for_all_forms()

        from .utils import download_comitati_discendenti, download_excel
        if action == 'print':
            return typeform.print()
        elif action == 'download':
            return download_excel(sede, comitato, request.path)
        else:
            return download_comitati_discendenti(sede, request.path)

    if id_regionale:
        struttura = OrderedDict()
        regionale = Sede.objects.get(pk=id_regionale)
        comitati = regionale.ottieni_discendenti(includimi=True).filter(estensione__in=[LOCALE, REGIONALE, PROVINCIALE]).order_by(
            '-estensione')
        for comitato in comitati:
            if comitato.estensione == 'R':
                typeform_db = TypeFormCompilati.objects.filter(
                    Q(tipo__icontains='Regionali') & Q(comitato__pk=comitato.pk)).first()
                if typeform_db:
                    struttura[comitato] = 1
                else:
                    struttura[comitato] = 0
            else:
                typeform_db = TypeFormCompilati.objects.filter(
                    Q(tipo__icontains='Territoriali') & Q(comitato__pk=comitato.pk)).first()
                if typeform_db:
                    struttura[comitato] = 1
                else:
                    struttura[comitato] = 0
        context['struttura'] = struttura
    else:
        context['regionali'] = Sede.objects.filter(estensione=REGIONALE, attiva=True)
    return 'monitora_fabb_info_regionale.html', context


@xframe_options_exempt
@pagina_pubblica(permetti_embed=True)
def trasparenza_publica(request, me):
    context = {}
    id_regionale = request.GET.get('r', None)
    action = request.GET.get('action', None)
    comitato = request.GET.get('comitato', None)

    if action and comitato:
        sede = Sede.objects.get(pk=comitato)
        delegato = sede.delegati_monitoraggio_trasparenza()
        typeform = TypeFormResponsesTrasparenzaCheckPubblica(
            persona=delegato, comitato_id=sede.id, users_pk=delegato
        )
        typeform.get_responses_for_all_forms()
        if action == 'print':
            return typeform.print()
    if id_regionale:
        struttura = OrderedDict()
        regionale = Sede.objects.get(pk=id_regionale)
        locali = regionale.ottieni_discendenti(includimi=True).filter(estensione__in=[LOCALE, REGIONALE]).order_by(
            '-estensione')
        for locale in locali:
            typeform_db = TypeFormCompilati.objects.filter(
                Q(tipo__icontains='trasparenza') & Q(comitato__pk=locale.pk)).first()
            if typeform_db:
                struttura[locale] = 1
            else:
                struttura[locale] = 0

        context['struttura'] = struttura
    else:
        context['regionali'] = Sede.objects.filter(estensione=REGIONALE, attiva=True).exclude(pk=1638)

    return 'monitora_trasparenza_pubblica.html', context
