from django.contrib import admin

from .models import NotiziaTest, NotiziaTestSegmento


class NotiziaTestSegmentoInline(admin.TabularInline):
    model = NotiziaTestSegmento
    raw_id_fields=('notizia',)
    extra =1

@admin.register(NotiziaTest)
class AdminNotiziaTest(admin.ModelAdmin):
    inlines = (NotiziaTestSegmentoInline,)