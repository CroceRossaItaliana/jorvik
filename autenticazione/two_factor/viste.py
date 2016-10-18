# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import resolve_url, redirect
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from two_factor import signals
from two_factor.forms import BackupTokenForm
from two_factor.views import DisableView, LoginView, SetupView
from two_factor.views.utils import class_view_decorator


from .forms import JorvikAuthenticationTokenForm


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class JorvikDisableView(DisableView):

    redirect_url = reverse_lazy('two_factor:profile')


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class JorvikSetupView(SetupView):
    def get(self, request, *args, **kwargs):
        """
        Start the setup wizard. Redirect if already enabled.
        """
        return super(SetupView, self).get(request, *args, **kwargs)


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class JorvikLoginView(LoginView):

    form_list = (
        ('auth', AuthenticationForm),
        ('token', JorvikAuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def done(self, form_list, **kwargs):
        """
        Login the user and redirect to the desired page.
        """
        login(self.request, self.get_user())

        redirect_to = self.request.GET.get(self.redirect_field_name, '')
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        if self.get_user().richiedi_attivazione_2fa:
            redirect_to = resolve_url(settings.TWO_FACTOR_PROFILE)

        device = getattr(self.get_user(), 'otp_device', None)
        if device:
            signals.user_verified.send(sender=__name__, request=self.request,
                                       user=self.get_user(), device=device)
        return redirect(redirect_to)
