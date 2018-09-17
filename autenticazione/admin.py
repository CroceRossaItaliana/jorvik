from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin, Group
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from otp_yubikey.models import YubikeyDevice
from reversion.admin import VersionAdmin

from autenticazione.forms import ModuloModificaUtenza, ModuloCreazioneUtenza
from autenticazione.models import Utenza
from gruppi.readonly_admin import ReadonlyAdminMixin

__author__ = 'alfioemanuele'


class TOTPDeviceInlineAdmin(admin.TabularInline):
    model = TOTPDevice
    extra = 0
    readonly_fields = ('key', 'step', 't0', 'digits', 'tolerance', 'drift', 'name', 'confirmed', 'last_t')

    def has_add_permission(self, request):
        return False


class StaticDeviceInlineAdmin(admin.TabularInline):
    model = StaticDevice
    extra = 0
    readonly_fields = ('name', 'confirmed')

    def has_add_permission(self, request):
        return False


class YubikeyDeviceInlineAdmin(admin.TabularInline):
    model = YubikeyDevice
    extra = 0
    readonly_fields = ('private_id', 'key', 'session', 'counter', 'name', 'confirmed',)

    def has_add_permission(self, request):
        return False


@admin.register(Utenza)
class AdminUtenza(ReadonlyAdminMixin, VersionAdmin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser', 'richiedi_2fa',
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
    inlines = (TOTPDeviceInlineAdmin, StaticDeviceInlineAdmin, YubikeyDeviceInlineAdmin)
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
                'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'richiedi_2fa'
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
