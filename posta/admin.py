from django.contrib import admin, messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter

from gruppi.readonly_admin import ReadonlyAdminMixin

from .models import Messaggio, Destinatario


class InCodaFilter(SimpleListFilter):
    title = 'In coda'
    parameter_name = 'in_coda'

    def lookups(self,  request, model_admin):
        return [('24', '< 24 ore'),
                ('24-48', 'da 24 a 48 ore'),
                ('A', 'Tutti gli altri')]

    def queryset(self, request, queryset):
        now = timezone.now()
        h24 = timezone.timedelta(hours=24)
        timedelta_24 = now - h24
        timedelta_48 = now - (h24 * 2)

        qs = Messaggio.in_coda()

        if self.value() == '24':
            return qs.filter(creazione__lte=now, creazione__gt=timedelta_24)
        elif self.value() == '24-48':
            return qs.filter(creazione__lt=timedelta_24, creazione__gt=timedelta_48)
        elif self.value() == 'A':
            return qs.filter(creazione__lt=timedelta_48)


class AdminDestinatarioInline(ReadonlyAdminMixin, admin.TabularInline):
    model = Destinatario
    search_fields = ['messaggio__oggetto', 'persona__codice_fiscale', 'persona__email_contatto',
                     'persona__utenza__email', 'errore',]
    list_display = ('messaggio', 'persona', 'inviato', 'tentativo', 'errore', 'errore_codice', 'invalido')
    list_filter = ('inviato', 'tentativo', )
    raw_id_fields = ('persona', 'messaggio',)
    extra = 0


def force_sending_email(modeladmin, request, queryset):
    from .tasks import invia_mail_forzato

    qs_ids = tuple(queryset.values_list('pk', flat=True))
    applied_task_id = invia_mail_forzato.apply_async((qs_ids,))

    rescheduled_tasks_len = applied_task_id.get()

    # Restituisci messaggio di avviso
    if rescheduled_tasks_len == len(qs_ids):
        text = "<b>A tutti i messaggi è stato assegnato un task di rinvio.</b><br>"
        text += "Sono stati rinviati %s messaggi."
        # text += ''.join(list(map(lambda x: x+"<br>", rescheduled_tasks_id)))
        messages.success(request, mark_safe(text % rescheduled_tasks_len))
    else:
        text = "Sono stati assegnati solo %s task per %s messaggi"
        messages.warning(request, text % (rescheduled_tasks_len, len(qs_ids)))

force_sending_email.short_description = 'Invia le mail forzatamente'


@admin.register(Messaggio)
class AdminMessaggio(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['oggetto', 'mittente__codice_fiscale', 'mittente__email_contatto', 'mittente__utenza__email']
    list_display = ('oggetto', 'mittente', 'creazione', 'ultimo_tentativo', 'tentativi', 'terminato', 'task_id')
    list_filter = ('creazione', 'terminato', 'ultimo_tentativo', InCodaFilter)
    raw_id_fields = ('mittente', 'rispondi_a')
    inlines = [AdminDestinatarioInline, ]
    actions = [force_sending_email, ]


@admin.register(Destinatario)
class AdminDestinatario(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['messaggio__oggetto', 'persona__codice_fiscale', 'persona__email_contatto',
                     'persona__utenza__email', 'errore', 'errore_codice']
    list_display = ('messaggio', 'persona', 'inviato', 'tentativo', 'errore', 'errore_codice', 'invalido')
    list_filter = ('inviato', 'tentativo', 'errore_codice', 'invalido')
    raw_id_fields = ('persona', 'messaggio',)
