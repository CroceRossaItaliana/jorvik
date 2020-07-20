from datetime import date

from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from anagrafica.models import Persona, Appartenenza
from anagrafica.permessi.costanti import ERRORE_PERMESSI
from articoli.models import Articolo, ArticoloSegmento
from autenticazione.funzioni import pagina_privata, pagina_pubblica, VistaDecorata


def get_articoli(persona, anno=None, mese=None, query=None):
    filtri_extra = {}
    if query:
        filtri_extra['titolo__icontains'] = query
    if anno:
        filtri_extra['data_inizio_pubblicazione__year'] = anno
    if mese:
        filtri_extra['data_inizio_pubblicazione__month'] = mese
    if persona:
        articoli_segmenti = ArticoloSegmento.objects.all().filtra_per_segmenti(persona)
        articoli = articoli_segmenti.oggetti_collegati().pubblicati()
    else:
        articoli = Articolo.objects.pubblicati()

    return articoli.filter(**filtri_extra)


class FiltraSegmenti(object):

    @property
    def persona(self):
        try:
            return self.request.user.persona
        except (Persona.DoesNotExist, AttributeError):
            return None
        
    def get_anno(self):
        anno = self.kwargs.get('anno', '')
        if not anno:
            try:
                anno = int(self.request.GET.get('anno', ''))
            except ValueError:
                anno = ''
        return anno
        
    def get_mese(self):
        mese = self.kwargs.get('mese', '')
        if not mese:
            try:
                mese = int(self.request.GET.get('mese', ''))
            except ValueError:
                mese = ''
        return mese

    def get_queryset(self):
        anno = self.get_anno()
        mese = self.get_mese()
        persona = self.persona
        query = self.request.GET.get('q', '')
        return get_articoli(persona, anno, mese, query)


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
        anno = self.get_anno()
        mese = self.get_mese()
        anni = Articolo.objects.all().dates('data_inizio_pubblicazione', 'year', 'DESC')
        context['anni'] = [anno.year for anno in anni]
        context['mesi'] = [('%0d' % i, date(year=date.today().year, month=i, day=1)) for i in range(1, 12)]
        context['mese_selezionato'] = '%0s' % mese
        context['anno_selezionato'] = anno
        context['query'] = self.request.GET.get('q', '')
        return context


def articolo_protetto(*args, **kwargs):

    def _articolo_protetto(request, *pargs, **pkwargs):
        articolo = Articolo.objects.get(slug=pkwargs['articolo_slug'])
        func = None
        if not articolo.segmenti.exists():
            func = pagina_pubblica(*args, **kwargs)
        else:
            func = pagina_privata(*args, **kwargs)
        return func(request, *pargs, **pkwargs)

    return _articolo_protetto


class DettaglioArticolo(FiltraSegmenti, VistaDecorata, DetailView):
    model = Articolo
    slug_field = 'slug'
    slug_url_kwarg = 'articolo_slug'
    context_object_name = 'articolo'

    @method_decorator(articolo_protetto)
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(DettaglioArticolo, self).dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(ERRORE_PERMESSI)

    def get_template_names(self):
        if self.request.user.is_authenticated():
            return 'dettaglio_articolo.html'
        else:
            return 'dettaglio_articolo_pubblico.html'

    def get_object(self, queryset=None):
        obj = super(DetailView, self).get_object(queryset)
        if obj:
            obj.incrementa_visualizzazioni()
        return obj
