# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.timezone import now

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class Require2FA(MiddlewareMixin):

    def _aggiorna_ultima_azione(self, request):
        request.user.ultima_azione = now()
        request.user.save()

    def process_request(self, request):
        if request.user.is_anonymous():
            return
        # URL non soggette a nessun controllo perché view di servizio
        urls = [request.path_info.startswith(resolve_url(url)) for url in settings.TWO_FACTOR_PUBLIC]

        # Se è richiesta la 2FA e non è attivata si forza l'utente ad attivarla
        if not any(urls) and request.user.is_authenticated() and request.user.richiedi_attivazione_2fa:
            return HttpResponseRedirect(settings.TWO_FACTOR_PROFILE)

        # Controllo sulla durata della sessione per gli amministratori
        limite = now() - timedelta(seconds=settings.TWO_FACTOR_SESSION_DURATA*60)
        # per tutte le altre pagine facciamo il check
        if not any(urls) and request.user.is_staff and request.user.richiedi_2fa:
            if request.user.ultima_azione and request.user.ultima_azione < limite:
                # sessione scaduta -> si manda a pagina di avviso
                logout(request)
                return HttpResponseRedirect(settings.TWO_FACTOR_SESSIONE_SCADUTA)
            elif request.path_info != settings.TWO_FACTOR_SESSIONE_SCADUTA:
                # si rinnova la sessione
                self._aggiorna_ultima_azione(request)

    def process_response(self, request, response):
        if request.path_info.startswith(resolve_url(settings.LOGIN_URL)) and request.user.is_staff and request.user.richiedi_2fa:
            self._aggiorna_ultima_azione(request)

        return response
