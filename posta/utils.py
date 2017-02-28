from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from anagrafica.models import Persona


def imposta_destinatari_e_scrivi_messaggio(request, qs_destinatari=Persona.objects.none()):
    qs_destinatari = Persona.objects.filter(pk__in=qs_destinatari.values_list('id', flat=True))
    request.session["messaggio_destinatari"] = qs_destinatari
    request.session["messaggio_destinatari_timestamp"] = datetime.now()
    return redirect(reverse('posta-scrivi'))
