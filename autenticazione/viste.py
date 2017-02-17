# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.contrib.auth.views import logout as original_logout
from loginas import settings as la_settings
from loginas.utils import restore_original_login


def logout(request, next_page=None, template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME, extra_context=None):
    """
    This can replace your default logout view. In you settings, do:

    from django.core.urlresolvers import reverse_lazy
    LOGOUT_URL = reverse_lazy('logout')
    """
    original_session = request.session.get(la_settings.USER_SESSION_FLAG)

    if original_session:
        restore_original_login(request)
        return redirect(la_settings.LOGOUT_REDIRECT)
    else:
        return original_logout(request, next_page, template_name, redirect_field_name, extra_context)
