from django.contrib import admin

from articoli.models import Articolo, ArticoloSegmento


class ArticoloSegmentoInline(admin.TabularInline):
    model = ArticoloSegmento
    extra = 1


@admin.register(Articolo)
class AdminArticolo(admin.ModelAdmin):
    inlines = (ArticoloSegmentoInline,)
    readonly_fields = ('visualizzazioni',)
    actions = ['pubblica', 'bozza']
    fieldsets = (
        (None, {
            'fields': ('titolo', 'slug', 'corpo', 'estratto',)
        }),
        ('Informazioni', {
            'fields': ('autore', 'data_inizio_pubblicazione', 'data_fine_pubblicazione','stato', 'visualizzazioni'),
        }),
    )

    def pubblica(self, request, queryset):
        rows_updated = queryset.update(stato=Articolo.PUBBLICATO)
        if rows_updated == 1:
            message_bit = "1 articolo è stato"
        else:
            message_bit = "%s articoli sono stati" % rows_updated
        self.message_user(request, "%s pubblicati con successo." % message_bit)
    pubblica.short_description = "Pubblica uno o più articoli"

    def bozza(self, request, queryset):
        rows_updated = queryset.update(stato=Articolo.BOZZA)
        if rows_updated == 1:
            message_bit = "1 articolo è stato"
        else:
            message_bit = "%s articoli sono stati" % rows_updated
        self.message_user(request, "%s passato allo stato bozza con successo." % message_bit)
    spubblica.short_description = "Passa allo stato bozza uno o più articoli"
