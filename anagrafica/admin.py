from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.admin import GenericTabularInline
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.six import text_type
from django.utils.translation import ungettext_lazy

from mptt.admin import MPTTModelAdmin

from autenticazione.models import Utenza
from base.admin import InlineAutorizzazione
from gruppi.readonly_admin import ReadonlyAdminMixin
from .models import Persona, Sede, Appartenenza, Delega, Documento,\
    Fototessera, Estensione, Trasferimento, Riserva, Dimissione, Telefono, \
    ProvvedimentoDisciplinare



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
    actions = ['sposta_persone',]

    messaggio_spostamento = ungettext_lazy(
        '%(num)s persona trasferita con successo', '%(num)s persone trasferite con successo', 'num'
    )

    def _has_transfer_permission(self, request, obj=None):
        change_permission = Persona._meta.app_label + '.' + get_permission_codename('transfer', Persona._meta)
        return request.user.has_perm(change_permission)

    def get_actions(self, request):
        actions = super(AdminPersona, self).get_actions(request)
        if not self._has_transfer_permission(request) and 'sposta_persone' in actions:
            del actions['sposta_persone']
        return actions

    def get_urls(self):
        urls = super(AdminPersona, self).get_urls()
        custom_urls = [
            url(r'^trasferisci/$',
                self.admin_site.admin_view(self.sposta_persone_csv),
                name='anagrafica_persona_trasferisci'),
            url(r'^trasferisci_azione/$',
                self.admin_site.admin_view(self.sposta_persone_post),
                name='anagrafica_persona_trasferisci_post'),
            url(r'^report/conoscenza/$',
                self.admin_site.admin_view(self.conoscneza_report),
                name='anagrafica_persona_report_conoscneza'),
        ]


        return custom_urls + urls

    def conoscneza_report(self, request):
        import csv
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=Report-conoscneza-%s.csv' % datetime.now()

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Nome Cognome', 'Data Creazione Utenza',
                         'Codice Fiscale', 'Citta', 'Provincia', 'Conoscenza'])

        queryset = Persona.objects.filter(conoscenza__isnull=False)
        for persona in queryset:
            writer.writerow([
                persona.nome_completo,
                persona.creazione.date(),
                persona.codice_fiscale,
                persona.comune_residenza,
                persona.provincia_residenza,
                persona.get_conoscenza_display() or 'Non impostato'
            ])

        return response

    def _sposta_persone(self, request, form_class, queryset=None):
        from anagrafica.forms import ModuloSpostaPersoneManuale, ModuloSpostaPersoneDaCSV

        contesto = {}
        trasferimenti = None
        esclusi = None
        errori = None
        eseguito = False
        if not self._has_transfer_permission(request):
            self.message_user(request, 'Non si hanno i diritti per l\'operazione richiesta', level=messages.WARNING)
            return HttpResponseRedirect(reverse('admin:anagrafica_persona_changelist'))

        if request.method.lower() == 'post':
            if form_class == ModuloSpostaPersoneDaCSV:
                form = form_class(request.POST, files=request.FILES)
                contesto.update({
                    'url': reverse('admin:anagrafica_persona_trasferisci'),
                })
                if form.is_valid():
                    if form.cleaned_data.get('procedi', False) and request.session.get('dati_persone', None):
                        trasferimenti = form.sposta_persone(request.user.persona, persone=request.session['dati_persone'])
                        errori = [persona for persona in trasferimenti if persona[1] is not True and isinstance(persona[1], text_type)]
                        trasferimenti = [persona[0] for persona in trasferimenti if persona[1] is True or isinstance(persona[1], Appartenenza)]
                        self.message_user(request, self.messaggio_spostamento % {'num': len(trasferimenti)})
                        contesto.update({
                            'title': 'Esito dei trasferimenti',
                        })
                        eseguito = True
                    else:
                        dati, esclusi = form.elenco_persone(request.FILES['dati'])
                        form.fields['dati'].widget = forms.HiddenInput()
                        form.data['procedi'] = 1
                        request.session['dati_persone'] = dati
                        contesto.update({
                            'title': 'Conferma trasferimenti',
                            'etichetta_invio': 'Avvia trasferimento',
                            'dati_csv': dati,
                        })
            elif form_class == ModuloSpostaPersoneManuale:
                if 'do_action' in request.POST and request.POST.get(helpers.ACTION_CHECKBOX_NAME, ''):
                    form = form_class(request.POST)
                    queryset = Persona.objects.filter(
                        pk__in=[int(pk) for pk in request.POST.get(helpers.ACTION_CHECKBOX_NAME, '').split(',')]
                    )

                    # Escludiamo i non volontari
                    volontari = Appartenenza.objects.filter(
                        Appartenenza.query_attuale(membro=Appartenenza.VOLONTARIO).q,
                        persona__in=queryset
                    ).values_list('persona', flat=True)
                    esclusi = queryset.exclude(pk__in=volontari)
                    queryset = queryset.filter(pk__in=volontari)
                    if form.is_valid():
                        persone, scarti = form.mappa_persone(queryset)
                        trasferimenti = form.sposta_persone(request.user.persona, persone=persone)
                        errori = [persona for persona in trasferimenti if persona[1] is not True and isinstance(persona[1], text_type)]
                        trasferimenti = [persona[0] for persona in trasferimenti if persona[1] is True or isinstance(persona[1], Appartenenza)]
                        self.message_user(request, self.messaggio_spostamento % {'num': len(trasferimenti)})
                    contesto.update({
                        'title': 'Esito dei trasferimenti',
                        'url': reverse('admin:anagrafica_persona_trasferisci_post'),
                    })
                else:
                    form = form_class()
                    contesto.update({
                        'title': 'Seleziona gli estremi dei trasferimenti',
                        'etichetta_invio': 'Avvia trasferimento',
                        'eseguito': False,
                        'dati_pronti': True,
                        'queryset': queryset,
                        'url': reverse('admin:anagrafica_persona_trasferisci_post'),
                    })
                eseguito = 'do_action' in request.POST
        else:
            if form_class == ModuloSpostaPersoneDaCSV:
                contesto = {
                    'title': 'Carica dati dei trasferimenti',
                    'etichetta_invio': 'Carica dati',
                    'eseguito': False,
                    'url': reverse('admin:anagrafica_persona_trasferisci'),
                }
            elif form_class == ModuloSpostaPersoneManuale:
                contesto.update({
                    'title': 'Seleziona gli estremi dei trasferimenti',
                    'etichetta_invio': 'Avvia trasferimento',
                    'eseguito': False,
                    'url': reverse('admin:anagrafica_persona_trasferisci_post'),
                })
                eseguito = 'do_action' in request.POST
            form = form_class()

        contesto.update({
            'opts': self.model._meta,
            'form': form,
            'queryset': queryset,
            'action': 'sposta_persone',
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'pks': queryset.values_list('pk', flat=True) if queryset else '',
            'trasferimenti': trasferimenti,
            'errori': errori,
            'esclusi': esclusi,
            'eseguito': eseguito,
        })
        return render(request, 'admin/anagrafica/trasferimento_massivo.html', contesto)

    def sposta_persone_post(self, request):
        from anagrafica.forms import ModuloSpostaPersoneManuale
        return self._sposta_persone(request, ModuloSpostaPersoneManuale)

    def sposta_persone(self, request, queryset):
        from anagrafica.forms import ModuloSpostaPersoneManuale
        return self._sposta_persone(request, ModuloSpostaPersoneManuale, queryset)

    def sposta_persone_csv(self, request):
        from anagrafica.forms import ModuloSpostaPersoneDaCSV
        return self._sposta_persone(request, ModuloSpostaPersoneDaCSV)


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
    list_display = ("persona", 'inizio', 'fine', 'motivo',)
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
    raw_id_fields = ['persona', 'registrato_da', 'sede',]

