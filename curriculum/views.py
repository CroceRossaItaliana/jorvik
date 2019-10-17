from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from anagrafica.permessi.incarichi import INCARICO_GESTIONE_TITOLI
from autenticazione.funzioni import pagina_privata
from base.errori import  errore_nessuna_appartenenza
from formazione.constants import FORMAZIONE_ROLES
from .forms import FormAddQualificaCRI
from .models import Titolo, TitoloPersonale


@pagina_privata
def cdf_titolo_json(request, me):
    if request.is_ajax and me.deleghe_attuali(tipo__in=FORMAZIONE_ROLES).exists():
        area_id = request.POST.get('area', None)
        cdf_livello = request.POST.get('cdf_livello', None)

        if cdf_livello and area_id:
            query = Titolo.objects.filter(is_active=True,
                                          area=area_id[0],
                                          cdf_livello=cdf_livello[0]).exclude(sigla__in=['CRI',])
            options_for_select = {option['id']: {
                'nome': option['nome'],
                'description': option['description'],
                'prevede_esame': option['scheda_prevede_esame'],
            } for option in query.values('id', 'nome', 'description', 'scheda_prevede_esame')}

            return JsonResponse(options_for_select)

    return JsonResponse({})


@pagina_privata
def cv_add_qualifica_cri(request, me):
    redirect_url = redirect('/utente/curriculum/TC/')

    if request.method == 'POST':
        form = FormAddQualificaCRI(request.POST, request.FILES, me=me)
        if form.is_valid():
            cd = form.cleaned_data
            titolo = cd['titolo']
            qualifica_nuova = TitoloPersonale(persona=me, confermata=False, **cd)
            qualifica_nuova.save()

            if titolo.richiede_conferma:
                sede_attuale = me.sede_riferimento()
                if not sede_attuale:
                    qualifica_nuova.delete()
                    return errore_nessuna_appartenenza(request, me, torna_url="/utente/curriculum/TC/")

                qualifica_nuova.autorizzazione_richiedi_sede_riferimento(me, INCARICO_GESTIONE_TITOLI)

            messages.success(request, "La qualifica è stata inserita.")
            return redirect_url

        return 'cv_add_qualifica_cri.html', {'form': form}

    return redirect_url
