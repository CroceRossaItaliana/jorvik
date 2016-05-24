from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from autenticazione.funzioni import pagina_privata, VistaDecorata, pagina_pubblica
from ckeditor_filebrowser_filer.views import _return_thumbnail
from filer.models import File, Folder
from filer.server.views import filer_settings

from gestione_file.models import Documento, DocumentoSegmento, Immagine
from jorvik import settings

server = filer_settings.FILER_PRIVATEMEDIA_SERVER


class ListaDocumenti(VistaDecorata, ListView):
    model = Documento
    template_name = 'lista_documenti.html'
    context_object_name = 'documenti'
    paginate_by = 10

    @method_decorator(pagina_privata)
    def dispatch(self, request, *args, **kwargs):
        return super(ListaDocumenti, self).dispatch(request, *args, **kwargs)

    @property
    def persona(self):
        return self.request.user.persona

    def get_queryset(self):
        cartella = self.kwargs.get('cartella', None)
        documenti_segmenti = DocumentoSegmento.objects.all().filtra_per_segmenti(self.persona)
        documenti = documenti_segmenti.oggetti_collegati()
        stringa = self.request.GET.get('q', '')
        if stringa:
            filtri_extra = Q(name__icontains=stringa) | Q(original_filename__icontains=stringa)
            return documenti.filter(filtri_extra)
        elif cartella:
            filtri_extra = {
                'folder': cartella
            }
            return documenti.filter(**filtri_extra)
        return documenti.none()

    def get_context_data(self, **kwargs):
        context = super(ListaDocumenti, self).get_context_data(**kwargs)
        cartella = self.kwargs.get('cartella', None)
        context['livello_superiore'] = 'root'
        if cartella:
            context['cartella'] = Folder.objects.get(pk=cartella)
            context['livello_superiore'] = context['cartella'].parent
        if cartella:
            filtri = {
                'parent__pk': cartella,
            }
        else:
            filtri = {
                'parent__isnull': True
            }
        if not self.request.GET.get('q', ''):
            context['cartelle'] = Folder.objects.filter(**filtri)
        else:
            context['query'] = self.request.GET.get('q', '')
        if cartella:
            context['url_vista'] = reverse('lista_documenti', kwargs={'cartella': cartella})
        else:
            context['url_vista'] = reverse('lista_documenti')
        return context


@pagina_privata
def serve_protected_file(request, persona, pk):
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


@pagina_pubblica
def serve_image(request, persona, image_id, thumb_options=None, width=None, height=None):
    """
    returns the content of an image sized according to the parameters
    :param request: Request object
    :param image_id: Filer image ID
    :param thumb_options: ThumbnailOption ID
    :param width: user-provided width
    :param height: user-provided height
    :return: JSON serialized URL components ('url', 'width', 'height')
    """
    image = Immagine.objects.get(pk=image_id)
    if getattr(image, 'canonical_url', None):
        url = image.canonical_url
    else:
        url = image.url
    thumb = _return_thumbnail(image, thumb_options, width, height)
    if thumb:
        return server.serve(request, file_obj=thumb, save_as=False)
    else:
        return HttpResponseRedirect(url)