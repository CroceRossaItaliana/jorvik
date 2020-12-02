from django.http import JsonResponse
from autenticazione.funzioni import pagina_privata
from curriculum.models import Titolo
from formazione.constants import FORMAZIONE_ROLES
from formazione.models import CorsoBase


@pagina_privata
def cdf_titolo_json(request, me):
    if request.is_ajax and me.deleghe_attuali(tipo__in=FORMAZIONE_ROLES).exists():
        area_id = request.POST.get('area', None)
        cdf_livello = request.POST.get('cdf_livello', None)
        tipo = request.POST.get('tipo', None)

        if cdf_livello and area_id:
            query = Titolo.objects.filter(is_active=True,
                                          area=area_id[0],
                                          cdf_livello=cdf_livello[0]).exclude(sigla__in=['CRI',])

            if tipo == CorsoBase.CORSO_ONLINE:
                query = query.filter(modalita_titoli_cri=Titolo.CORSO_ONLINE)
            elif tipo == CorsoBase.CORSO_NUOVO:
                query = query.filter(modalita_titoli_cri=Titolo.CORSO_BASE)

            elif tipo == CorsoBase.CORSO_EQUIPOLLENZA:
                query = query.filter(modalita_titoli_cri=Titolo.CORSO_EQUIPOLLENZA)

            print(query)

            options_for_select = {option['id']: {
                'nome': option['nome'],
                'description': option['description'],
                'prevede_esame': option['scheda_prevede_esame'],
            } for option in query.values('id', 'nome', 'description', 'scheda_prevede_esame')}

            return JsonResponse(options_for_select)

    return JsonResponse({})
