# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class Require2FA(MiddlewareMixin):
    def process_request(self, request):
        urls = [request.path_info.startswith(resolve_url(url)) for url in settings.TWO_FACTOR_PUBLIC ]
        if not any(urls) and request.user.is_authenticated() and request.user.richiedi_attivazione_2fa:
            return HttpResponseRedirect(settings.TWO_FACTOR_PROFILE)
