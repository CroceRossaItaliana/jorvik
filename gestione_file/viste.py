from django.contrib.auth.models import AnonymousUser
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from gestione_file.models import Documento, DocumentoSegmento


class ListaDocumenti(ListView):
    model = Documento
    context_object_name = 'documenti'
    template_name = 'lista_documenti.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        filtri_extra = {}
        context = super(ListaDocumenti, self).get_context_data(**kwargs)
        if 'q' in self.request.GET:
            filtri_extra['name__icontains'] = self.request.GET['q']
        utente = self.request.user
        if isinstance(utente, AnonymousUser):
            return None # TODO: redirect in a proper way
        persona = utente.persona
        documenti_segmenti = DocumentoSegmento.objects.all().filtra_per_segmenti(persona)
        documenti = documenti_segmenti.oggetti_collegati().filter(**filtri_extra)
        context['documenti'] = documenti
        return context
