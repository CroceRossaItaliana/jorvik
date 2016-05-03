from django.contrib.auth.models import AnonymousUser
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from articoli.models import Articolo


class ListaArticoli(ListView):
    model = Articolo
    context_object_name = 'articoli'
    template_name = 'lista_articoli.html'
    paginate_by = 10

    def get_queryset(self):
        filtri_extra = {}
        anno = self.kwargs.get('anno')
        mese = self.kwargs.get('mese')
        if 'date' in self.request.GET:
            data = self.request.GET['date']
        if 'anno' in self.request.GET:
            anno = self.request.GET['anno']
        if 'mese' in self.request.GET:
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
        articoli = Articolo.objects.pubblicati().filter(**filtri_extra)

        id_articoli = []
        if persona:
            for articolo in articoli:
                segmenti = articolo.segmenti.all()
                if not segmenti:
                    id_articoli.append(articolo.pk)
                    continue
                appartiene = False
                for segmento in segmenti:
                    if persona.appartiene_al_segmento(segmento):
                        appartiene = True
                        break
                if appartiene:
                    id_articoli.append(articolo.pk)
        if id_articoli:
            articoli = articoli.filter(pk__in=id_articoli)
        return articoli

    def get_context_data(self, **kwargs):
        context = super(ListaArticoli, self).get_context_data(**kwargs)
        anni = Articolo.objects.pubblicati().extra(select={'anno': 'extract( year from data_inizio_pubblicazione )'}).values_list('anno', flat=True).order_by().annotate(Count('id'))
        anni = [int(anno) for anno in anni]
        context['anni'] = anni
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
        if persona:
            segmenti = obj.segmenti.all()
            if not segmenti:
                obj.incrementa_visualizzazioni()
                return obj
            for segmento in segmenti:
                if persona.appartiene_al_segmento(segmento):
                    obj.incrementa_visualizzazioni()
                    return obj
            return None
        obj.incrementa_visualizzazioni()
        return obj
