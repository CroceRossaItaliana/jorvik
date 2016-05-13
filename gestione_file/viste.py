from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from autenticazione.funzioni import pagina_privata, VistaDecorata
from filer.models import File, Folder
from filer.server.views import filer_settings

from gestione_file.models import Documento, DocumentoSegmento
from jorvik import settings

server = filer_settings.FILER_PRIVATEMEDIA_SERVER


class ListaDocumenti(VistaDecorata, ListView):
    model = Documento
    template_name = 'lista_documenti.html'
    paginate_by = 10

    @method_decorator(pagina_privata)
    def dispatch(self, request, *args, **kwargs):
        return super(ListaDocumenti, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListaDocumenti, self).get_context_data(**kwargs)
        utente = self.request.user
        persona = utente.persona
        filtri = {
            'parent__isnull': True
        }
        cartella_pk = self.kwargs.get('cartella_pk', None)
        documenti_segmenti = DocumentoSegmento.objects.all().filtra_per_segmenti(persona)
        documenti = documenti_segmenti.oggetti_collegati()
        context['livello_superiore'] = 'root'
        if cartella_pk:
            context['cartella'] = Folder.objects.get(pk=cartella_pk)
            context['livello_superiore'] = context['cartella'].parent
            filtri = {
                'parent__pk': cartella_pk,
            }
            filtri_extra = {
                'folder': cartella_pk
            }
            context['documenti'] = documenti.filter(**filtri_extra)
        cartelle_root = Folder.objects.filter(**filtri)
        context['cartelle'] = cartelle_root
        if 'q' in self.request.GET:
            stringa = self.request.GET['q']
            filtri_extra = Q(name__icontains=stringa) | Q(original_filename__icontains=stringa)
            del context['cartelle']
            context['documenti'] = documenti.filter(filtri_extra)
        if cartella_pk:
            context['url_vista'] = reverse('lista_documenti', kwargs={'cartella_pk': cartella_pk})
        else:
            context['url_vista'] = reverse('lista_documenti')
        return context


def serve_protected_file(request, pk):
    """
    Restituisce il file e incrementa il numero di downloads
    """
    try:
        file_obj = File.objects.get(pk=int(pk))
        file_obj.incrementa_downloads()
    except File.DoesNotExist:
        raise Http404('File not found')
    if file_obj.url_documento:
        return HttpResponsePermanentRedirect(file_obj.url_documento)
    if not file_obj.has_read_permission(request):
        if settings.DEBUG:
            raise PermissionDenied
        else:
            raise Http404('File not found')
    return server.serve(request, file_obj=file_obj.file, save_as=False)
