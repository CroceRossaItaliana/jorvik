from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from autenticazione.forms import ModuloModificaUtenza, ModuloCreazioneUtenza
from autenticazione.models import Utenza

__author__ = 'alfioemanuele'

class AdminUtenza(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                 'groups', 'user_permissions')}),
        ('Utenza', {'fields': ('persona',)}),
        ('Date importanti', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    form = ModuloModificaUtenza
    add_form = ModuloCreazioneUtenza
    list_display = ('email', 'is_staff')
    search_fields = ('email', 'persona')
    ordering = ('email',)



admin.site.register(Utenza, AdminUtenza)
