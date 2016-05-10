from django import forms
from django.contrib import admin

from articoli.models import Articolo, ArticoloSegmento


class ArticoloSegmentoInline(admin.TabularInline):
    model = ArticoloSegmento
    extra = 1
    raw_id_fields = ('sede', 'titolo')


class ArticoloAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ArticoloAdminForm, self).__init__(*args, **kwargs)
        self.fields['estratto'].widget = forms.Textarea()
        self.fields['estratto'].help_text = 'L\'estratto è limitato a 1024 caratteri, il testo eccedente sarà tagliato'

    class Meta:
        model = Articolo
        fields = '__all__'


@admin.register(Articolo)
class AdminArticolo(admin.ModelAdmin):
    form = ArticoloAdminForm
    inlines = (ArticoloSegmentoInline,)
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
