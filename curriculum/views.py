from django.http import JsonResponse
from autenticazione.funzioni import pagina_privata
from curriculum.models import Titolo


@pagina_privata
def cdf_titolo_json(request, me):
    if request.is_ajax and me.is_presidente:
        area_id = request.POST.get('area', None)
        cdf_livello = request.POST.get('cdf_livello', None)

        if cdf_livello and area_id:
            query = Titolo.objects.filter(area=area_id[0], cdf_livello=cdf_livello[0])
            options_for_select = {option['id']: {
                    'nome': option['nome'],
                    'description': option['description']}
                for option in query.values('id', 'nome', 'description')}

            return JsonResponse(options_for_select)
