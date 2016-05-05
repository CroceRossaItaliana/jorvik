from django.contrib.auth.models import AnonymousUser
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from filer.models import Folder

from gestione_file.models import Documento, DocumentoSegmento


class ListaDocumenti(ListView):
    model = Documento
    context_object_name = 'documenti'
    template_name = 'lista_documenti.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ListaDocumenti, self).get_context_data(**kwargs)
        utente = self.request.user
        if isinstance(utente, AnonymousUser):
            return None # TODO: redirect in a proper way
        persona = utente.persona
        filtri = {
            'parent__isnull' : True
        }
        filtri_extra = {}
        cartella_pk = self.kwargs.get('cartella_pk')
        documenti_segmenti = DocumentoSegmento.objects.all().filtra_per_segmenti(persona)
        documenti = documenti_segmenti.oggetti_collegati()
        if cartella_pk:
            context['livello_superiore'] = Folder.objects.get(pk=cartella_pk).parent
            filtri = {
                'parent__pk': cartella_pk,
            }
            filtri_extra= {
                'folder': cartella_pk
            }
            context['documenti'] = documenti.filter(**filtri_extra)
        cartelle_root = Folder.objects.filter(**filtri)
        context['cartelle'] = cartelle_root
        if 'q' in self.request.GET:
            filtri_extra = {
                'name__icontains': self.request.GET['q']
            }
            del context['cartelle']
            context['documenti'] = documenti.filter(**filtri_extra)
        return context
