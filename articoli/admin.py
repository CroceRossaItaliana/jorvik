from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from articoli.models import Articolo, ArticoloSegmento
from base.models import Allegato
from gruppi.readonly_admin import ReadonlyAdminMixin


class ArticoloSegmentoInline(ReadonlyAdminMixin, admin.TabularInline):
    model = ArticoloSegmento
    extra = 1
    raw_id_fields = ('sede', 'titolo')


class ArticoloAdminForm(ReadonlyAdminMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ArticoloAdminForm, self).__init__(*args, **kwargs)
        self.fields['estratto'].widget = forms.Textarea()
        self.fields['estratto'].help_text = 'L\'estratto è limitato a 1024 caratteri, il testo eccedente sarà tagliato'

    class Meta:
        model = Articolo
        fields = '__all__'


class AllegatoInline(ReadonlyAdminMixin, GenericTabularInline):
    model = Allegato
    extra = 2
    ct_field = 'oggetto_tipo'
    ct_fk_field = 'oggetto_id'


@admin.register(Articolo)
class AdminArticolo(ReadonlyAdminMixin, admin.ModelAdmin):
    form = ArticoloAdminForm
    inlines = (ArticoloSegmentoInline, AllegatoInline)
    readonly_fields = ('visualizzazioni',)
    actions = ['pubblica', 'bozza']
    fieldsets = (
        (None, {
            'fields': ('titolo', 'corpo', 'estratto',)
        }),
        ('Informazioni', {
            'fields': (
                'data_inizio_pubblicazione', 'data_fine_pubblicazione', 'stato', 'visualizzazioni'
            ),
        }),
    )
    list_filter = ('stato', 'data_inizio_pubblicazione', 'data_fine_pubblicazione',)
    search_fields = ('titolo',)
    list_display = ('titolo', 'stato', 'data_inizio_pubblicazione', 'visualizzazioni', 'segmenti_testo')

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj:
            for inline_class in self.inlines:
                inline = inline_class(self.model, self.admin_site)
                if request:
                    if not (inline.has_add_permission(request) or
                            inline.has_change_permission(request, obj) or
                            inline.has_delete_permission(request, obj)):
                        continue
                    if not inline.has_add_permission(request):
                        inline.max_num = 0
                inline_instances.append(inline)

        return inline_instances

    def pubblica(self, request, queryset):
        rows_updated = queryset.update(stato=Articolo.PUBBLICATO)
        if rows_updated == 1:
            message_bit = '1 articolo è stato'
        else:
            message_bit = '%s articoli sono stati' % rows_updated
        self.message_user(request, '%s pubblicati con successo.' % message_bit)
    pubblica.short_description = 'Pubblica uno o più articoli'

    def bozza(self, request, queryset):
        rows_updated = queryset.update(stato=Articolo.BOZZA)
        if rows_updated == 1:
            message_bit = '1 articolo è stato'
        else:
            message_bit = '%s articoli sono stati' % rows_updated
        self.message_user(request, '%s passato allo stato bozza con successo.' % message_bit)
    bozza.short_description = 'Passa allo stato bozza uno o più articoli'


@admin.register(ArticoloSegmento)
class AdminArticoloSegmento(ReadonlyAdminMixin, admin.ModelAdmin):
    pass
