from datetime import date

from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from articoli.models import Articolo, ArticoloSegmento
from autenticazione.funzioni import pagina_privata


class ListaArticoli(ListView):
    model = Articolo
    context_object_name = 'articoli'
    template_name = 'lista_articoli.html'
    paginate_by = 10

    @method_decorator(pagina_privata)
    def dispatch(self, request, *args, **kwargs):
        return super(ListaArticoli, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        filtri_extra = {}
        context = super(ListaArticoli, self).get_context_data(**kwargs)
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
        utente = self.request.user
        persona = utente.persona
        articoli_segmenti = ArticoloSegmento.objects.all().filtra_per_segmenti(persona)
        articoli = articoli_segmenti.oggetti_collegati().pubblicati().filter(**filtri_extra)
        anni = articoli.extra(select={'anno': 'extract( year from data_inizio_pubblicazione )'}).values_list('anno', flat=True).order_by().annotate(Count('id'))
        anni = sorted(set([int(anno) for anno in anni] + [date.today().year]))
        context['anni'] = anni
        context['mesi'] = [('%0d' % i, date(year=date.today().year, month=i, day=1)) for i in range(1, 12)]
        context['mese_selezionato'] = '%0s' % mese
        context['anno_selezionato'] = anno
        context['articoli'] = articoli
        return context


class DettaglioArticolo(DetailView):
    model = Articolo
    slug_field = 'slug'
    slug_url_kwarg = 'articolo_slug'
    context_object_name = 'articolo'
    template_name = 'dettaglio_articolo.html'

    @method_decorator(pagina_privata)
    def dispatch(self, request, *args, **kwargs):
        return super(DettaglioArticolo, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        utente = self.request.user
        persona = utente.persona
        obj = super(DetailView, self).get_object()
        articoli_segmenti = ArticoloSegmento.objects.all().filtra_per_segmenti(persona)
        articoli = articoli_segmenti.oggetti_collegati().pubblicati().filter(pk=obj.pk)
        if articoli.count() == 1:
            obj.incrementa_visualizzazioni()
            return obj
