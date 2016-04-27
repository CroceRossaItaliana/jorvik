# -*- coding: utf-8 -*-
import os.path

from django.contrib import admin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from filer import settings as filer_settings
from filer.admin import FileAdmin, ImageAdmin, FolderAdmin
from filer.models import File, Folder
from filer.utils.loader import load_object
from filer.admin.tools import AdminContext, popup_status

from .models import Documento, Immagine

admin.site.unregister(Folder)


class AdminCartella(FolderAdmin):
    directory_listing_template = 'admin/gestione_file/lista_cartelle.html'


admin.site.register(Folder, AdminCartella)


class AdminDocumento(FileAdmin):
    add_form_template = 'admin/gestione_file/form_aggiungi.html'
    change_form_template = 'admin/filer/file/change_form.html'
    extra_main_fields = ('url_documento',)
    extra_advanced_fields = ()
    extra_fieldsets = ()
    fieldsets = None

    def has_add_permission(self, request):
        return admin.ModelAdmin.has_add_permission(self, request)

    def save_model(self, request, obj, form, change):
        """
        Imposta alcune proprietà di base del file quando viene creato manualmente
        Inoltre adatta il tipo di oggetto in base all'estensione effettiva
        """
        # Le personalizzazioni valgono solo se l'oggetto non è stato ancora salvato
        if not obj.pk:
            if not obj.original_filename:
                obj.original_filename = os.path.basename(obj.path)
            if not obj.owner_id:
                obj.owner_id = request.user.pk
            if not obj.is_public:
                obj.is_public = filer_settings.FILER_IS_PUBLIC_DEFAULT
            try:
                obj.folder_id = int(request.GET.get('parent_id', None))
            except TypeError:
                pass
            # codice analogo a filer.admin.clipboardadmin per la gestione dei tipi
            for filer_class in filer_settings.FILER_FILE_MODELS:
                FileSubClass = load_object(filer_class)
                if obj.file and FileSubClass.matches_file_type(obj.file.path, None, request):
                    break
            else:
                FileSubClass = load_object(filer_settings.FILER_FILE_MODELS[-1])
            ConcreteFileClass = FileSubClass
            if ConcreteFileClass:
                new = ConcreteFileClass()
                for k, v in obj.__dict__.items():
                    new.__dict__[k] = v
                super(AdminDocumento, self).save_model(request, new, form, change)
                obj.pk = new.pk
                return
        super(AdminDocumento, self).save_model(request, obj, form, change)

    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        """
        Effettua l'override del metodo nella classe genitore che altrimenti non consentirebbe
        l'uso del template corretto add_form_template
        """
        extra_context = {'show_delete': True,
                         'is_popup': popup_status(request),
                         'filer_admin_context': AdminContext(request)}
        context.update(extra_context)
        return super(FileAdmin, self).render_change_form(
            request=request, context=context, add=add, change=change,
            form_url=form_url, obj=obj)

    def response_post_save_add(self, request, obj):
        """
        Ricalcola l'URL a cui redirigere sulla base del tipo concreto di oggetto creato
        """
        # qualunque file venga creato deve sempre essere rediretto alla changelist della
        # cartella di riferimento o all'elenco dei file senza cartella
        if obj.folder:
            post_url = reverse('admin:filer-directory_listing', kwargs={
                'folder_id': obj.folder.id
            })
        else:
            post_url = reverse('admin:filer-directory_listing-unfiled_images')
        if not obj.file or Immagine.matches_file_type(obj.file.path, None, request):
            obj = File.objects.non_polymorphic().get(pk=obj.pk)
        opts = obj._meta
        if self.has_change_permission(request, None):
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url
            )
        else:
            post_url = reverse(
                'admin:index', current_app=self.admin_site.name
            )
        return HttpResponseRedirect(post_url)


AdminDocumento.fieldsets = AdminDocumento.build_fieldsets(
    extra_main_fields=('url_documento',),
)

admin.site.register(Documento, AdminDocumento)


class AdminImmagine(ImageAdmin):
    add_form_template = 'admin/gestione_file/form_aggiungi.html'
    change_form_template = 'admin/filer/image/change_form.html'


AdminImmagine.fieldsets = AdminImmagine.build_fieldsets(
    extra_main_fields=('default_alt_text', 'default_caption', 'url_documento'),
    extra_fieldsets=(
        ('Subject Location', {
            'fields': ('subject_location',),
            'classes': ('collapse',),
        }),
    )
)

admin.site.register(Immagine, AdminImmagine)
