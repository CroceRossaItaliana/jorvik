# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from datetime import timedelta

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.timezone import now

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class Require2FA(MiddlewareMixin):
    def process_request(self, request):
        # URL non soggette a nessun controllo perché view di servizio
        urls = [request.path_info.startswith(resolve_url(url)) for url in settings.TWO_FACTOR_PUBLIC ]

        # Se è richiesta la 2FA e non è attivata si forza l'utente ad attivarla
        if not any(urls) and request.user.is_authenticated() and request.user.richiedi_attivazione_2fa:
            return HttpResponseRedirect(settings.TWO_FACTOR_PROFILE)

        # Controllo sulla durata della sessione per gli amministratori
        limite = now() - timedelta(seconds=settings.TWO_FACTOR_SESSION_DURATA*60)
        if any(urls) and request.user.is_staff and request.user.richiedi_2fa:
            request.user.ultima_azione = now()
            request.user.save()
        if not any(urls) and request.user.is_staff and request.user.richiedi_2fa:
            if request.user.ultima_azione and request.user.ultima_azione < limite:
                return HttpResponseRedirect(settings.TWO_FACTOR_SESSIONE_SCADUTA)
            else:
                request.user.ultima_azione = now()
                request.user.save()
