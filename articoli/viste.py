from django.contrib.auth.models import AnonymousUser
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from articoli.models import Articolo, ArticoloSegmento


class ListaArticoli(ListView):
    model = Articolo
    context_object_name = 'articoli'
    template_name = 'lista_articoli.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        filtri_extra = {}
        context = super(ListaArticoli, self).get_context_data(**kwargs)
        anno = self.kwargs.get('anno')
        mese = self.kwargs.get('mese')
        if 'date' in self.request.GET:
            data = self.request.GET['date']
        if 'anno' in self.request.GET:
            anno = self.request.GET['anno']
        if 'mese' in self.request.GET and 'anno' in self.request.GET:
            mese = self.request.GET['mese']
        if 'q' in self.request.GET:
            filtri_extra['titolo__icontains'] = self.request.GET['q']
        if anno:
            filtri_extra['data_inizio_pubblicazione__year'] = anno
        if mese:
            filtri_extra['data_inizio_pubblicazione__month'] = mese
        utente = self.request.user
        if isinstance(utente, AnonymousUser):
            return None
        persona = utente.persona
        articoli_segmenti = ArticoloSegmento.objects.all().filtra_per_segmenti(persona)
        articoli = articoli_segmenti.oggetti_collegati().pubblicati().filter(**filtri_extra)
        anni = articoli.extra(select={'anno': 'extract( year from data_inizio_pubblicazione )'}).values_list('anno', flat=True).order_by().annotate(Count('id'))
        anni = [int(anno) for anno in anni]
        context['anni'] = anni
        context['articoli'] = articoli
        return context


class DettaglioArticolo(DetailView):
    model = Articolo
    slug_field = 'slug'
    slug_url_kwarg = 'articolo_slug'
    context_object_name = 'articolo'
    template_name = 'dettaglio_articolo.html'

    def get_object(self):
        utente = self.request.user
        if isinstance(utente, AnonymousUser):
            return None
        persona = utente.persona
        obj = super(DetailView, self).get_object()
        articoli_segmenti = ArticoloSegmento.objects.all().filtra_per_segmenti(persona)
        articoli = articoli_segmenti.oggetti_collegati().pubblicati().filter(pk=obj.pk)
        if articoli.count() == 1:
            obj.incrementa_visualizzazioni()
            return obj
