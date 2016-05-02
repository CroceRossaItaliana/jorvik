from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from articoli.models import Articolo


class ListaArticoli(ListView):
    model = Articolo
    context_object_name = 'articoli'
    template_name = 'lista_articoli.html'

    def get_queryset(self):
        filtri_extra = {}
        anno = self.kwargs.get('anno')
        mese = self.kwargs.get('mese')
        if 'date' in self.request.GET:
            data = self.request.GET['date']
            if not '-' in data:
                anno = data
            else:
                data = data.split('-')
                mese = data[0]
                anno = data[1]
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
