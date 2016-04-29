from django.contrib import admin

from articoli.models import Articolo, ArticoloSegmento


class ArticoloSegmentoInline(admin.TabularInline):
    model = ArticoloSegmento
    extra = 1


@admin.register(Articolo)
class AdminArticolo(admin.ModelAdmin):
    inlines = (ArticoloSegmentoInline,)
    readonly_fields = ('visualizzazioni',)
    fieldsets = (
        (None, {
            'fields': ('titolo', 'slug', 'corpo', 'estratto',)
        }),
        ('Informazioni', {
            'fields': ('autore', 'data_inizio_pubblicazione', 'data_fine_pubblicazione','stato', 'visualizzazioni'),
        }),
    )
