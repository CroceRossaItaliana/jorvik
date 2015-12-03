from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from anagrafica.models import Persona, Sede, Appartenenza, Delega, Documento, Fototessera, Estensione, Trasferimento

RAW_ID_FIELDS_PERSONA = []
RAW_ID_FIELDS_SEDE = []
RAW_ID_FIELDS_APPARTENENZA = ['persona', 'sede', 'precedente']
RAW_ID_FIELDS_DELEGA = ['persona', 'firmatario', ]
RAW_ID_FIELDS_DOCUMENTO = ['persona']
RAW_ID_FIELDS_FOTOTESSERA = ['persona']
RAW_ID_FIELDS_ESTENSIONE = ["persona", "richiedente", "destinazione", "appartenenza"]
RAW_ID_FIELDS_TRASFERIMENTO = ["persona", "richiedente", "destinazione", "appartenenza"]


# Aggiugni al pannello di amministrazione
class InlineAppartenenzaPersona(admin.TabularInline):
    model = Appartenenza
    raw_id_fields = RAW_ID_FIELDS_APPARTENENZA
    extra = 0


class InlineDelegaPersona(admin.TabularInline):
    model = Delega
    raw_id_fields = RAW_ID_FIELDS_DELEGA
    fk_name = 'persona'
    extra = 0


class InlineDocumentoPersona(admin.TabularInline):
    model = Documento
    raw_id_fields = RAW_ID_FIELDS_DOCUMENTO
    extra = 0


@admin.register(Persona)
class AdminPersona(admin.ModelAdmin):
    search_fields = ['nome', 'cognome', 'codice_fiscale', 'utenza__email', 'email_contatto']
    list_display = ('nome', 'cognome', 'utenza', 'email_contatto', 'codice_fiscale', 'data_nascita', 'stato', 'ultima_modifica', )
    list_filter = ('stato', )
    inlines = [InlineAppartenenzaPersona, InlineDelegaPersona, InlineDocumentoPersona]


@admin.register(Sede)
class AdminSede(MPTTModelAdmin):
    search_fields = ['nome', 'genitore__nome']
    list_display = ('nome', 'genitore', 'tipo', 'estensione', 'creazione', 'ultima_modifica', )
    list_filter = ('tipo', 'estensione', 'creazione', )

# admin.site.register(Appartenenza)

@admin.register(Appartenenza)
class AdminAppartenenza(admin.ModelAdmin):
    search_fields = ["membro", "persona__nome", "persona__cognome", "persona__codice_fiscale",
                     "persona__utenza__email", "sede__nome"]
    list_display = ("persona", "sede", "attuale", "inizio", "fine", "creazione")
    list_filter = ("membro", "inizio", "fine")
    raw_id_fields = RAW_ID_FIELDS_APPARTENENZA


# admin.site.register(Delega)
@admin.register(Delega)
class AdminDelega(admin.ModelAdmin):
    search_fields = ["tipo", "persona__nome", "persona__codice_fiscale", "tipo", "oggetto_id"]
    list_display = ("tipo", "oggetto", "persona", "inizio", "fine", "attuale")
    list_filter = ("tipo", "inizio", "fine")
    raw_id_fields = RAW_ID_FIELDS_DELEGA


# admin.site.register(Documento)
@admin.register(Documento)
class AdminDocumento(admin.ModelAdmin):
    search_fields = ["tipo", "persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("tipo", "persona", "creazione")
    list_filter = ("tipo", "persona", "creazione")
    raw_id_fields = RAW_ID_FIELDS_DOCUMENTO


# admin.site.register(Fototessera)
@admin.register(Fototessera)
class AdminFototessera(admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "persona__codice_fiscale"]
    list_display = ("persona", "creazione", "esito")
    list_filter = ("persona",)
    raw_id_fields = RAW_ID_FIELDS_FOTOTESSERA


# admin.site.register(Estensione)
@admin.register(Estensione)
class AdminEstensione(admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome", "richiedente", "destinazione"]
    list_display = ("persona",)
    list_filter = ("persona",)
    raw_id_fields = RAW_ID_FIELDS_ESTENSIONE


# admin.site.register(Trasferimento)
@admin.register(Trasferimento)
class AdminTrasferimento(admin.ModelAdmin):
    search_fields = ["persona__nome", "persona__cognome",  "richiedente", "destinazione"]
    list_display = ("persona",)
    list_filter = ("persona",)
    raw_id_fields = RAW_ID_FIELDS_TRASFERIMENTO
