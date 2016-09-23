from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from mptt.admin import MPTTModelAdmin
from anagrafica.models import Persona, Sede, Appartenenza, Delega, Documento, Fototessera, Estensione, Trasferimento, \
    Riserva, Dimissione, Telefono, ProvvedimentoDisciplinare
from autenticazione.models import Utenza
from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin


RAW_ID_FIELDS_PERSONA = []
RAW_ID_FIELDS_SEDE = []
RAW_ID_FIELDS_APPARTENENZA = ['persona', 'sede', 'precedente', 'vecchia_sede']
RAW_ID_FIELDS_DELEGA = ['persona', 'firmatario', ]
RAW_ID_FIELDS_DOCUMENTO = ['persona']
RAW_ID_FIELDS_FOTOTESSERA = ['persona']
RAW_ID_FIELDS_ESTENSIONE = ["persona", "richiedente", "destinazione", "appartenenza"]
RAW_ID_FIELDS_TRASFERIMENTO = ["persona", "richiedente", "destinazione", "appartenenza"]
RAW_ID_FIELDS_RISERVA = ['persona', 'appartenenza']
RAW_ID_FIELDS_DIMISSIONE = ['persona', 'appartenenza', 'richiedente', 'sede']
RAW_ID_FIELDS_TELEFONO = ['persona']


# Aggiugni al pannello di amministrazione
class InlineAppartenenzaPersona(ReadonlyAdminMixin, admin.TabularInline):
    model = Appartenenza
    raw_id_fields = RAW_ID_FIELDS_APPARTENENZA
    extra = 0


class InlineDelegaPersona(ReadonlyAdminMixin, admin.TabularInline):
    model = Delega
    raw_id_fields = RAW_ID_FIELDS_DELEGA
    fk_name = 'persona'
    extra = 0


class InlineDelegaSede(ReadonlyAdminMixin, GenericTabularInline):
    model = Delega
    raw_id_fields = RAW_ID_FIELDS_DELEGA
    ct_field = 'oggetto_tipo'
    ct_fk_field = 'oggetto_id'
    extra = 0


class InlineDocumentoPersona(ReadonlyAdminMixin, admin.TabularInline):
    model = Documento
    raw_id_fields = RAW_ID_FIELDS_DOCUMENTO
    extra = 0


class InlineUtenzaPersona(ReadonlyAdminMixin, admin.StackedInline):
    model = Utenza
    extra = 0


class InlineTelefonoPersona(ReadonlyAdminMixin, admin.StackedInline):
    model = Telefono
    extra = 0


@admin.register(Persona)
class AdminPersona(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['nome', 'cognome', 'codice_fiscale', 'utenza__email', 'email_contatto', '=id',]
    list_display = ('nome', 'cognome', 'utenza', 'email_contatto', 'codice_fiscale', 'data_nascita', 'stato',
                    'ultima_modifica', )
    list_filter = ('stato', )
    list_display_links = ('nome', 'cognome', 'codice_fiscale',)
    inlines = [InlineUtenzaPersona, InlineAppartenenzaPersona, InlineDelegaPersona, InlineDocumentoPersona, InlineTelefonoPersona]


@admin.register(Sede)
class AdminSede(ReadonlyAdminMixin, MPTTModelAdmin):
    search_fields = ['nome', 'genitore__nome']
    list_display = ('nome', 'genitore', 'tipo', 'estensione', 'creazione', 'ultima_modifica', )
    list_filter = ('tipo', 'estensione', 'creazione', )
    raw_id_fields = ('genitore', 'locazione',)
    list_display_links = ('nome', 'estensione',)
    inlines = [InlineDelegaSede,]

# admin.site.register(Appartenenza)

@admin.register(Appartenenza)
class AdminAppartenenza(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["membro", "persona__nome", "persona__cognome", "persona__codice_fiscale",
                     "persona__utenza__email", "sede__nome"]
    list_display = ("persona", "sede", "attuale", "inizio", "fine", "creazione")
    list_filter = ("membro", "inizio", "fine")
    raw_id_fields = RAW_ID_FIELDS_APPARTENENZA
    inlines = [InlineAutorizzazione]

# admin.site.register(Delega)
@admin.register(Delega)
class AdminDelega(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["tipo", "persona__nome", "persona__cognome", "persona__codice_fiscale", "tipo", "oggetto_id"]
    list_display = ("tipo", "oggetto", "persona", "inizio", "fine", "attuale")
    list_filter = ("tipo", "inizio", "fine")
    raw_id_fields = RAW_ID_FIELDS_DELEGA


# admin.site.register(Documento)
@admin.register(Documento)
class AdminDocumento(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["tipo", "persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("tipo", "persona", "creazione")
    list_filter = ("tipo", "creazione")
    raw_id_fields = RAW_ID_FIELDS_DOCUMENTO


# admin.site.register(Fototessera)
@admin.register(Fototessera)
class AdminFototessera(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("persona", "creazione", "esito")
    list_filter = ("creazione",)
    raw_id_fields = RAW_ID_FIELDS_FOTOTESSERA
    inlines = [InlineAutorizzazione]



# admin.site.register(Estensione)
@admin.register(Estensione)
class AdminEstensione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale", "destinazione__nome"]
    list_display = ("persona", "destinazione", "richiedente", )
    list_filter = ("confermata", "ritirata", "creazione",)
    raw_id_fields = RAW_ID_FIELDS_ESTENSIONE
    inlines = [InlineAutorizzazione]


# admin.site.register(Trasferimento)
@admin.register(Trasferimento)
class AdminTrasferimento(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome",  "persona__codice_fiscale", "destinazione__nome"]
    list_display = ("persona", "destinazione", "creazione", )
    list_filter = ("creazione", "confermata", "ritirata",)
    raw_id_fields = RAW_ID_FIELDS_TRASFERIMENTO
    inlines = [InlineAutorizzazione]


# admin.site.register(Riserva)
@admin.register(Riserva)
class AdminRiserva(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("persona",)
    list_filter = ("confermata", "ritirata", "creazione",)
    raw_id_fields = RAW_ID_FIELDS_RISERVA
    inlines = [InlineAutorizzazione]


# admin.site.register(Riserva)
@admin.register(Dimissione)
class AdminDimissione(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("persona", "richiedente")
    list_filter = ("creazione",)
    raw_id_fields = RAW_ID_FIELDS_DIMISSIONE
    inlines = [InlineAutorizzazione]


@admin.register(Telefono)
class AdminTelefono(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("persona", "numero", "servizio", "creazione",)
    list_filter = ("servizio", "creazione",)
    raw_id_fields = RAW_ID_FIELDS_TELEFONO


@admin.register(ProvvedimentoDisciplinare)
class AdminProvvedimentoDisciplinare(ReadonlyAdminMixin, admin.ModelAdmin):
    pass
