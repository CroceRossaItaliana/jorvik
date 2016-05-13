from datetime import date

from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from articoli.models import Articolo, ArticoloSegmento
from autenticazione.funzioni import pagina_privata, VistaDecorata


class FiltraSegmenti(object):

    @property
    def persona(self):
        return self.request.user.persona

    def get_queryset(self):
        filtri_extra = {}
        anno = self.kwargs.get('anno', '')
        mese = self.kwargs.get('mese', '')
        if not anno:
            try:
                anno = int(self.request.GET.get('anno', ''))
            except ValueError:
                pass
        if anno and not mese:
            try:
                mese = int(self.request.GET.get('mese', ''))
            except ValueError:
                pass
        filtri_extra['titolo__icontains'] = self.request.GET.get('q', '')
        if anno:
            filtri_extra['data_inizio_pubblicazione__year'] = anno
        if mese:
            filtri_extra['data_inizio_pubblicazione__month'] = mese
        articoli_segmenti = ArticoloSegmento.objects.all().filtra_per_segmenti(self.persona)
        articoli = articoli_segmenti.oggetti_collegati().pubblicati()
        return articoli.filter(**filtri_extra)


class ListaArticoli(FiltraSegmenti, VistaDecorata, ListView):
    model = Articolo
    context_object_name = 'articoli'
    template_name = 'lista_articoli.html'
    paginate_by = 10

    @method_decorator(pagina_privata)
    def dispatch(self, request, *args, **kwargs):
        return super(ListaArticoli, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListaArticoli, self).get_context_data(**kwargs)
        anno = self.kwargs.get('anno', '')
        mese = self.kwargs.get('mese', '')
        anni = self.get_queryset().dates('data_inizio_pubblicazione', 'year', 'DESC')
        context['anni'] = [anno.year for anno in anni]
        context['mesi'] = [('%0d' % i, date(year=date.today().year, month=i, day=1)) for i in range(1, 12)]
        context['mese_selezionato'] = '%0s' % mese
        context['anno_selezionato'] = anno
        context['query'] = self.request.GET.get('q', '')
        return context


class DettaglioArticolo(FiltraSegmenti, VistaDecorata, DetailView):
    model = Articolo
    slug_field = 'slug'
    slug_url_kwarg = 'articolo_slug'
    context_object_name = 'articolo'
    template_name = 'dettaglio_articolo.html'

    @method_decorator(pagina_privata)
    def dispatch(self, request, *args, **kwargs):
        return super(DettaglioArticolo, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(DetailView, self).get_object(queryset)
        if obj:
            obj.incrementa_visualizzazioni()
        return obj
