from django.http import JsonResponse
from autenticazione.funzioni import pagina_privata
from curriculum.models import Titolo


@pagina_privata
def cdf_titolo_json(request, me):
    if request.is_ajax:
        area_id = request.POST.get('area', None)
        cdf_livello = request.POST.get('cdf_livello', None)

        if cdf_livello and area_id:
            q = Titolo.objects.filter(area=area_id[0], cdf_livello=cdf_livello[0])

            return JsonResponse(dict(q.values_list('id', 'nome')))
