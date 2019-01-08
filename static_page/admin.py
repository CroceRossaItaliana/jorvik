from django.contrib import admin

from .models import Page


@admin.register(Page)
class AdminCorsoBase(admin.ModelAdmin):
    list_display = ['title', 'slug',]
