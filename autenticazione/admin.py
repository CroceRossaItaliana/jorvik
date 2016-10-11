from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin, Group
from autenticazione.forms import ModuloModificaUtenza, ModuloCreazioneUtenza
from autenticazione.models import Utenza
from gruppi.readonly_admin import ReadonlyAdminMixin

__author__ = 'alfioemanuele'


@admin.register(Utenza)
class AdminUtenza(ReadonlyAdminMixin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                 'groups', 'user_permissions')}),
        ('Utenza', {'fields': ('persona',)}),
        ('Date importanti', {'fields': ('last_login', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
    form = ModuloModificaUtenza
    add_form = ModuloCreazioneUtenza
    list_display = ('persona', 'email', 'ultimo_accesso', 'is_active', 'is_staff')
    search_fields = ('=id', 'email', 'persona__nome', 'persona__cognome', 'persona__codice_fiscale',)
    ordering = ('email',)
    raw_id_fields = ('persona', )

    # Permette login come utente
    change_form_template = 'loginas/change_form.html'

    def get_readonly_fields(self, request, obj=None):
        readonly = super(AdminUtenza, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return list(readonly) + [
                'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions'
            ]
        return readonly


class AdminGruppo(ReadonlyAdminMixin, GroupAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly = super(AdminGruppo, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return list(readonly) + [
                'permissions'
            ]
        return readonly

admin.site.unregister(Group)
admin.site.register(Group, AdminGruppo)
